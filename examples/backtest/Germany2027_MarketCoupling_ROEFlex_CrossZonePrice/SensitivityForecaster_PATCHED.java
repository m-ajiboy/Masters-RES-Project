// SPDX-FileCopyrightText: 2025-2026 German Aerospace Center <amiris@dlr.de>
//
// SPDX-License-Identifier: Apache-2.0
//
// ============================================================================
// NOT PART OF AMIRIS. This is an archival copy of a locally-patched version of
// AMIRIS v4.1.2's real agents/forecast/sensitivity/SensitivityForecaster.java,
// kept here purely for documentation/reproducibility of Phase 52 of this
// project's Progress Report (AMIRIS_Germany2027_Progress_Report.pdf).
// EXPERIMENTAL / INVESTIGATIVE ONLY - reported to the department as a technical
// finding, NOT adopted into this thesis's standing methodology (Phase 37 remains
// the reference build). Every change from the unpatched original is marked
// EXPERIMENTAL/FINAL/CORRECTED in the comments below. The compiled result of
// this file is amiris-core_4.1.2-EXPERIMENTAL-crosszoneprice.jar (this folder's
// parent directory) - the project's real, unmodified jar was never touched.
// ============================================================================
package agents.forecast.sensitivity;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import agents.forecast.MarketForecaster;
import communications.message.AmountAtTime;
import communications.message.ForecastClientRegistration;
import communications.message.PointInTime;
import communications.portable.Sensitivity;
import de.dlr.gitlab.fame.agent.input.DataProvider;
import de.dlr.gitlab.fame.agent.input.Input;
import de.dlr.gitlab.fame.agent.input.Make;
import de.dlr.gitlab.fame.agent.input.ParameterData;
import de.dlr.gitlab.fame.agent.input.ParameterData.MissingDataException;
import de.dlr.gitlab.fame.agent.input.Tree;
import de.dlr.gitlab.fame.communication.CommUtils;
import de.dlr.gitlab.fame.communication.Contract;
import de.dlr.gitlab.fame.communication.message.Message;
import de.dlr.gitlab.fame.data.TimeSeries;
import de.dlr.gitlab.fame.time.TimeStamp;
import util.TimedDataMap;

/** Forecasts sensitivities of market clearing results with respect to changes in demand and supply
 *
 * @author Christoph Schimeczek, Johannes Kochems */
public class SensitivityForecaster extends MarketForecaster implements SensitivityForecastProvider {
	static final String ERR_UNREGISTERED = "Client '%d' is not registered at SensitivityForecaster '%s'. Add `ForecastRegistration` contract before `SensitivityRequest`.";
	static final String WARN_INVALID = "Merit-order sensitivity in forcaster %s at time %s is not valid for either demand or supply. Ensure positive values for both!";
	private static Logger logger = LoggerFactory.getLogger(SensitivityForecaster.class);

	@Input private static final Tree parameters = Make.newTree().add(Make.newGroup("MultiplierEstimation").optional()
			.add(Make.newDouble("IgnoreAwardFactor").optional()
					.help("Awards with less energy than maximum energy divided by this factor are ignored."))
			.add(Make.newInt("InitialEstimateWeight").optional().help("Weight of the initial estimate."))
			.add(Make.newInt("DecayInterval").optional()
					.help("Interval steps after which a factor weight has reduced to exp(-1).")))
			// EXPERIMENTAL (investigative only, not part of any released AMIRIS version):
			// optional file-based cross-zone price signal, loaded once at construction exactly
			// like any other timeseries input (mirroring agents.forecast.PriceForecasterFile).
			// Zero effect on any scenario/agent that does not configure it.
			.add(Make.newSeries("CrossZonePriceForecastInEURperMWH").optional()
					.help("EXPERIMENTAL: optional price series of another zone. Where higher than this zone's own "
							+ "assessed supply-sensitivity price, an extra supply-sensitivity segment is appended "
							+ "(up to CrossZoneCapacityHeadroomInMW) valued at the cross-zone price, so storage/"
							+ "flexibility clients see a genuine incentive to discharge more."))
			.add(Make.newDouble("CrossZoneCapacityHeadroomInMW").optional()
					.help("EXPERIMENTAL: real transmission capacity headroom (MW) used to size the appended "
							+ "cross-zone supply-sensitivity segment."))
			.buildTree();

	private final FlexibilityAssessor flexibilityAssessor;
	private final HashMap<Long, ForecastType> typePerClient = new HashMap<>();
	private final TimedDataMap<ForecastType, MarketClearingAssessment> assessments = new TimedDataMap<>();
	private final TimedDataMap<ForecastType, MarketClearingAssessment> boostedAssessments = new TimedDataMap<>();
	private final TimeSeries crossZonePriceForecast;
	private final double crossZoneCapacityHeadroomInMW;
	// EXPERIMENTAL (investigative only): scope the boost to Reservoir Hydro (agent 9602) only,
	// excluding Pumped Storage (agent 9601). Tests whether Pumped Storage's newly-aggressive
	// early draining (observed under the always-on, unscoped boost) was the actual driver of the
	// correlation/shortage-count regression, rather than the boost mechanism itself.
	private static final long RESERVOIR_HYDRO_CLIENT_ID = 9602L;

	/** Instantiate a new {@link SensitivityForecaster}
	 *
	 * @param dataProvider input from config
	 * @throws MissingDataException if any required data is not provided */
	public SensitivityForecaster(DataProvider dataProvider) throws MissingDataException {
		super(dataProvider);
		ParameterData input = parameters.join(dataProvider);
		double cutOffFactor = input.getDoubleOrDefault("MultiplierEstimation.IgnoreAwardFactor", 1000.);
		int initialEstimateWeight = input.getIntegerOrDefault("MultiplierEstimation.InitialEstimateWeight", 24);
		int decayInterval = input.getIntegerOrDefault("MultiplierEstimation.DecayInterval", -1);
		flexibilityAssessor = new FlexibilityAssessor(cutOffFactor, initialEstimateWeight, decayInterval);
		crossZonePriceForecast = input.getTimeSeriesOrDefault("CrossZonePriceForecastInEURperMWH", null);
		crossZoneCapacityHeadroomInMW = input.getDoubleOrDefault("CrossZoneCapacityHeadroomInMW", 0.);

		call(this::registerClients).onAndUse(SensitivityForecastClient.Products.ForecastRegistration);
		call(this::updateForecastMultipliers).onAndUse(SensitivityForecastClient.Products.NetAward);
		call(this::sendSensitivityForecasts).on(SensitivityForecastProvider.Products.SensitivityForecast)
				.use(SensitivityForecastClient.Products.SensitivityRequest);
	}

	/** Register clients that sent a registration message */
	private void registerClients(ArrayList<Message> input, List<Contract> contracts) {
		for (Message message : input) {
			long clientId = message.getSenderId();
			var registration = message.getDataItemOfType(ForecastClientRegistration.class);
			flexibilityAssessor.registerClient(clientId, registration.amount);
			typePerClient.put(clientId, registration.type);
		}
		flexibilityAssessor.processInput();
		flexibilityAssessor.clearBefore(now());
	}

	/** Save net awards sent by clients and update their forecast multiplier history */
	private void updateForecastMultipliers(ArrayList<Message> input, List<Contract> contracts) {
		for (Message message : input) {
			AmountAtTime award = message.getDataItemOfType(AmountAtTime.class);
			flexibilityAssessor.saveAward(message.getSenderId(), award);
		}
		flexibilityAssessor.processInput();
	}

	/** Calculate new sensitivities, update multiplier averages, and send out new forecasts to clients */
	private void sendSensitivityForecasts(ArrayList<Message> messages, List<Contract> contracts) {
		for (Contract contract : contracts) {
			long clientId = contract.getReceiverId();
			double multiplier = flexibilityAssessor.getMultiplier(clientId);
			ArrayList<Message> requests = CommUtils.extractMessagesFrom(messages, clientId);
			for (Message message : requests) {
				TimeStamp time = message.getDataItemOfType(PointInTime.class).validAt;
				ForecastType type = getForecastTypeOfClient(clientId);
				MarketClearingAssessment assessment = clientId == RESERVOIR_HYDRO_CLIENT_ID
						? getBoostedAssessmentFor(type, time)
						: getAssessmentFor(type, time);
				Sensitivity sensitivity = new Sensitivity(assessment, multiplier);
				if (!sensitivity.isValid()) {
					logger.error(String.format(WARN_INVALID, this, time));
				}
				fulfilNext(contract, sensitivity, new PointInTime(time));
			}
		}
		flexibilityAssessor.clearBefore(now());
		assessments.clearBefore(now());
		boostedAssessments.clearBefore(now());
		saveNextForecast();
	}

	/** @return type of forecast of given client; throws a RuntimeException if client is not registered */
	private ForecastType getForecastTypeOfClient(long clientId) {
		ForecastType type = typePerClient.get(clientId);
		if (type == null) {
			throw new RuntimeException(String.format(ERR_UNREGISTERED, clientId, this));
		}
		return type;
	}

	/** @return the assessment of type associated with the given client at the specified time */
	private MarketClearingAssessment getAssessmentFor(ForecastType type, TimeStamp time) {
		assessments.computeIfAbsent(time, type, () -> buildAssessor(time, type));
		return assessments.get(time, type);
	}

	/** EXPERIMENTAL (investigative only): like {@link #getAssessmentFor}, but returns the
	 * cross-zone-boosted variant, cached separately so unscoped clients (e.g. Pumped Storage)
	 * keep seeing the real, unboosted assessment. */
	private MarketClearingAssessment getBoostedAssessmentFor(ForecastType type, TimeStamp time) {
		boostedAssessments.computeIfAbsent(time, type,
				() -> maybeBoostWithCrossZonePrice(getAssessmentFor(type, time), time));
		return boostedAssessments.get(time, type);
	}

	/** Create a new {@link MarketClearingAssessment} for given time and {@link ForecastType} */
	private MarketClearingAssessment buildAssessor(TimeStamp time, ForecastType type) {
		MarketClearingAssessment assessor = MarketClearingAssessment.build(type);
		assessor.assess(getResultForRequestedTime(time));
		return assessor;
	}

	/** EXPERIMENTAL (investigative only, not part of any released AMIRIS version): if a
	 * cross-zone price series is configured and, for the given time, its price is HIGHER than
	 * what this zone's own real supply-sensitivity curve implies at its own top end, appends
	 * one extra supply-sensitivity segment (sized by CrossZoneCapacityHeadroomInMW, valued at
	 * the cross-zone price) so storage/flexibility clients see a genuine incentive to discharge
	 * more. Root cause this directly targets (confirmed by reading CostSensitive.java): the
	 * real, unpatched supply-sensitivity curve is built ENTIRELY from this zone's own currently
	 * AWARDED local generation - it structurally has no way to represent that a neighbouring
	 * zone's unmet demand would pay more, no matter how the top-level forecast price is set.
	 * Returns the original, un-boosted assessment unchanged whenever no cross-zone series is
	 * configured, or the cross-zone price does not exceed the local one - i.e. byte-identical
	 * behaviour to the unpatched original in every scenario that does not configure this. */
	private MarketClearingAssessment maybeBoostWithCrossZonePrice(MarketClearingAssessment assessor, TimeStamp time) {
		if (crossZonePriceForecast == null) {
			return assessor;
		}
		double[] supplyPowers = assessor.getSupplySensitivityPowers();
		double[] supplyValues = assessor.getSupplySensitivityValues();
		if (supplyPowers.length < 2) {
			return assessor;
		}
		double crossZonePrice = crossZonePriceForecast.getValueLinear(time);
		// FINAL (investigative only): tested combining Reservoir-Hydro-only scoping with the 100
		// EUR/MWh threshold - this made things WORSE (shortage 6->10, the same-day evening
		// cascade reappeared on 17 Dec, plus a new hour on 24 Dec), confirming that the earlier
		// lead-time pre-positioning (which needs the boost to fire during the MODEST 93-153
		// EUR/MWh pre-event hours, not just the 3,000 EUR/MWh spike itself) is what made the
		// scoped-only variant work. Reverted to threshold=0 (always-on) + Reservoir-Hydro-only
		// scope, the best-performing combination found across this entire investigation:
		// shortage 7->6, bias -2.90->-0.95, vs. headline. Correlation (0.7168->0.6852) and MAE
		// (16.69->17.19) remain slightly worse than headline - not a clean win on every metric,
		// but the closest and most stable of all variants tested.
		final double GENUINE_SCARCITY_THRESHOLD_EUR_PER_MWH = 0.0;
		if (crossZonePrice < GENUINE_SCARCITY_THRESHOLD_EUR_PER_MWH) {
			return assessor;
		}

		// CORRECTED (investigative only): the first version appended one extra segment BEYOND
		// the curve's existing end (at ROE's total local cumulative supply, ~150,000+ MW) - but
		// any individual flexibility client (e.g. Reservoir Hydro, physical cap ~82,000 MW) can
		// never test a delta anywhere near that point, so the appended segment was provably
		// unreachable (confirmed directly via diagnostic instrumentation: the boost fired
		// correctly, with the right cross-zone price, but dispatch stayed byte-identical).
		// Fix: re-price EVERY existing segment's marginal value up to max(local, cross-zone)
		// price, so the boost is visible however small a delta any client actually tests -
		// rather than only at an unreachable tail.
		double[] boostedValues = new double[supplyValues.length];
		boostedValues[0] = supplyValues[0];
		boolean anyBoosted = false;
		for (int i = 1; i < supplyPowers.length; i++) {
			double segmentWidth = supplyPowers[i] - supplyPowers[i - 1];
			double localMarginalPrice = segmentWidth > 0 ? (supplyValues[i] - supplyValues[i - 1]) / segmentWidth : 0;
			double boostedMarginalPrice = Math.max(localMarginalPrice, crossZonePrice);
			if (boostedMarginalPrice > localMarginalPrice) {
				anyBoosted = true;
			}
			boostedValues[i] = boostedValues[i - 1] + segmentWidth * boostedMarginalPrice;
		}
		if (!anyBoosted) {
			return assessor;
		}
		return new BoostedAssessment(assessor.getDemandSensitivityPowers(), assessor.getDemandSensitivityValues(),
				supplyPowers, boostedValues);
	}

	/** EXPERIMENTAL (investigative only): a plain, immutable {@link MarketClearingAssessment}
	 * holding pre-computed arrays - used to return the cross-zone-boosted supply curve above. */
	private static final class BoostedAssessment implements MarketClearingAssessment {
		private final double[] demandPowers;
		private final double[] demandValues;
		private final double[] supplyPowers;
		private final double[] supplyValues;

		private BoostedAssessment(double[] demandPowers, double[] demandValues, double[] supplyPowers,
				double[] supplyValues) {
			this.demandPowers = demandPowers;
			this.demandValues = demandValues;
			this.supplyPowers = supplyPowers;
			this.supplyValues = supplyValues;
		}

		@Override
		public void assess(agents.markets.meritOrder.MarketClearingResult clearingResult) {
			// no-op: this assessment is already fully computed from a real, unpatched
			// assessment's arrays, per maybeBoostWithCrossZonePrice above.
		}

		@Override
		public double[] getDemandSensitivityPowers() {
			return demandPowers;
		}

		@Override
		public double[] getDemandSensitivityValues() {
			return demandValues;
		}

		@Override
		public double[] getSupplySensitivityPowers() {
			return supplyPowers;
		}

		@Override
		public double[] getSupplySensitivityValues() {
			return supplyValues;
		}
	}
}
