from abc import ABC, abstractmethod
from typing import List
from defs import CCIState

class DecisionAlgorithm(ABC):

    @abstractmethod
    def decide(self, current_hour: int, current_state: CCIState, hours_in_state: int, total_traffic_of_previous_hour: float) -> CCIState:
        pass

class SkiRentalLikeAlgorithm(DecisionAlgorithm):

    def __init__(self, contract_hours, k, c1, c2, delay_hours=72, cci_leasing_cost=0):
        """
        Initializes the algorithm with a memory window of k hours.
        """
        self.vpn_cost_history = []
        self.cci_cost_history = []
        self.k = k
        self.pairs = []
        self.vpn_thresh_log = []
        self.cci_thresh_log = []
        self.contract_hours = contract_hours
        self.current_state = CCIState.OFF
        self.c1 = c1
        self.c2 = c2
        self.delay_hours = delay_hours
        self.cci_leasing_cost = cci_leasing_cost

    def set_pairs(self, pairs: List['Pair']):
        """
                pairs: List[cci_decision.CciDecision.Pair],

        Sets the list of pairs to be used in decision making.

        :param pairs: List of traffic pairs with associated cost models.
        """
        self.pairs = pairs

    def _recent_vpn_cost(self, current_hour: int) -> float:
        """
        Calculates the sum of VPN costs over the last k hours.
        :param current_hour: The current simulation hour
        :return: Sum of VPN costs from [t-k, t]
        """
        start_hour = max(0, current_hour - self.k + 1)
        return sum(self.vpn_cost_history[start_hour:current_hour])

    def _recent_cci_cost(self, current_hour: int) -> float:
        """
        Calculates the sum of VPN costs over the last k hours.
        :param current_hour: The current simulation hour
        :return: Sum of VPN costs from [t-k, t]
        """
        start_hour = max(0, current_hour - self.k + 1)
        return sum(self.cci_cost_history[start_hour:current_hour])

    def decide(self, current_hour: int, current_state: CCIState, hours_in_state: int, total_traffic_of_previous_hour: float) -> CCIState:
        """
        Decides the next state of the CCI based on recent VPN costs.
        :param current_hour: The current simulation hour
        :param current_state: The current CCI state
        :param hours_in_state: Number of hours in the current state
        :param total_traffic_of_previous_hour: Traffic from the previous hour
        :param cost_model: Cost model for VPN and CCI
        :return: The next CCI state
        """
        total_vpn_cost = 0
        total_cci_cost = 0
        for pair in self.pairs:
            pair_traffic = pair.trace[current_hour - 1] if current_hour > 0 else 0
            if pair_traffic > 0:
                cost_v = pair.vpn_cost_per_hour + pair_traffic * pair.vpn_rate_per_gb
                cost_c = pair.vlan_cost_per_hour + pair_traffic * pair.cci_rate_per_gb
            else:
                cost_v = pair.vpn_cost_per_hour
                cost_c = pair.vlan_cost_per_hour
            total_vpn_cost += cost_v
            total_cci_cost += cost_c
        total_cci_cost += self.cci_leasing_cost
        self.vpn_cost_history.append(total_vpn_cost)
        self.cci_cost_history.append(total_cci_cost)
        recent_vpn_cost = self._recent_vpn_cost(current_hour)
        recent_cci_cost = self._recent_cci_cost(current_hour)
        self.vpn_thresh_log.append(recent_vpn_cost)
        self.cci_thresh_log.append(recent_cci_cost)
        if current_hour < 1:
            return CCIState.OFF
        if current_state == CCIState.OFF:
            if recent_cci_cost <= self.c1 * recent_vpn_cost:
                return CCIState.WAITING
        elif current_state == CCIState.WAITING:
            if hours_in_state >= self.delay_hours:
                return CCIState.ON
        elif current_state == CCIState.ON:
            if hours_in_state >= self.contract_hours:
                if recent_cci_cost <= self.c2 * recent_vpn_cost:
                    return CCIState.ON
                return CCIState.OFF
        return current_state

class monthlyDecisionAlgorithm(DecisionAlgorithm):

    def __init__(self, contract_hours, k, c1, c2, delay_hours=72, cci_leasing_cost=0):
        """
        Initializes the algorithm with a memory window of k hours.
        """
        self.vpn_cost_history = []
        self.cci_cost_history = []
        self.pairs = []
        self.vpn_thresh_log = []
        self.cci_thresh_log = []
        self.contract_hours = contract_hours
        self.current_state = CCIState.OFF
        self.c1 = c1
        self.c2 = c2
        self.delay_hours = delay_hours
        self.cci_leasing_cost = cci_leasing_cost

    def set_pairs(self, pairs: List['Pair']):
        """
                pairs: List[cci_decision.CciDecision.Pair],

        Sets the list of pairs to be used in decision making.

        :param pairs: List of traffic pairs with associated cost models.
        """
        self.pairs = pairs

    def _recent_vpn_cost(self, current_hour: int) -> float:
        """
        Calculates the sum of VPN costs over the last k hours.
        :param current_hour: The current simulation hour
        :return: Sum of VPN costs from [t-k, t]
        """
        start_hour = max(0, current_hour - 730 + 1)
        return sum(self.vpn_cost_history[start_hour:current_hour])

    def _recent_cci_cost(self, current_hour: int) -> float:
        """
        Calculates the sum of VPN costs over the last k hours.
        :param current_hour: The current simulation hour
        :return: Sum of VPN costs from [t-k, t]
        """
        start_hour = max(0, current_hour - 730 + 1)
        return sum(self.cci_cost_history[start_hour:current_hour])

    def decide(self, current_hour: int, current_state: CCIState, hours_in_state: int, total_traffic_of_previous_hour: float) -> CCIState:
        """
        Decides the next state of the CCI based on recent VPN costs.

        """
        total_vpn_cost = 0
        total_cci_cost = 0
        for pair in self.pairs:
            pair_traffic = pair.trace[current_hour - 1] if current_hour > 0 else 0
            if pair_traffic > 0:
                cost_v = pair.vpn_cost_per_hour + pair_traffic * pair.vpn_rate_per_gb
                cost_c = pair.vlan_cost_per_hour + pair_traffic * pair.cci_rate_per_gb
            else:
                cost_v = pair.vpn_cost_per_hour
                cost_c = pair.vlan_cost_per_hour
            total_vpn_cost += cost_v
            total_cci_cost += cost_c
        total_cci_cost += self.cci_leasing_cost
        self.vpn_cost_history.append(total_vpn_cost)
        self.cci_cost_history.append(total_cci_cost)
        if current_hour < 1:
            return CCIState.OFF
        if current_state == CCIState.WAITING:
            if hours_in_state >= self.delay_hours:
                return CCIState.ON
        if current_hour % 730 == 0:
            recent_vpn_cost = self._recent_vpn_cost(current_hour)
            recent_cci_cost = self._recent_cci_cost(current_hour)
            if recent_cci_cost <= recent_vpn_cost:
                return CCIState.WAITING
            else:
                return CCIState.OFF
        return current_state

class allHistoryAlgorithm(DecisionAlgorithm):

    def __init__(self, contract_hours, k, c1, c2, delay_hours=72, cci_leasing_cost=0):
        """
        Initializes the algorithm with a memory window of k hours.
        """
        self.vpn_cost_history = []
        self.cci_cost_history = []
        self.pairs = []
        self.vpn_thresh_log = []
        self.cci_thresh_log = []
        self.contract_hours = contract_hours
        self.current_state = CCIState.OFF
        self.c1 = c1
        self.c2 = c2
        self.delay_hours = delay_hours
        self.cci_leasing_cost = cci_leasing_cost

    def set_pairs(self, pairs: List['Pair']):
        """
                pairs: List[cci_decision.CciDecision.Pair],

        Sets the list of pairs to be used in decision making.

        :param pairs: List of traffic pairs with associated cost models.
        """
        self.pairs = pairs

    def _recent_vpn_cost(self, current_hour: int) -> float:
        """
        Calculates the sum of VPN costs over the last k hours.
        :param current_hour: The current simulation hour
        :return: Sum of VPN costs from [t-k, t]
        """
        start_hour = 0
        return sum(self.vpn_cost_history[0:current_hour])

    def _recent_cci_cost(self, current_hour: int) -> float:
        """
        Calculates the sum of VPN costs over the last k hours.
        :param current_hour: The current simulation hour
        :return: Sum of VPN costs from [t-k, t]
        """
        start_hour = 0
        return sum(self.cci_cost_history[start_hour:current_hour])

    def decide(self, current_hour: int, current_state: CCIState, hours_in_state: int, total_traffic_of_previous_hour: float) -> CCIState:
        """
        Decides the next state of the CCI based on recent VPN costs.

        """
        if current_hour < 1:
            return CCIState.OFF
        if current_state == CCIState.WAITING:
            if hours_in_state >= self.delay_hours:
                return CCIState.ON
            else:
                return CCIState.WAITING
        if current_state == CCIState.ON:
            return CCIState.ON
        total_vpn_cost = 0
        total_cci_cost = 0
        for pair in self.pairs:
            pair_traffic = pair.trace[current_hour - 1] if current_hour > 0 else 0
            if pair_traffic > 0:
                cost_v = pair.vpn_cost_per_hour + pair_traffic * pair.vpn_rate_per_gb
                cost_c = pair.vlan_cost_per_hour + pair_traffic * pair.cci_rate_per_gb
            else:
                cost_v = pair.vpn_cost_per_hour
                cost_c = pair.vlan_cost_per_hour
            total_vpn_cost += cost_v
            total_cci_cost += cost_c
        total_cci_cost += self.cci_leasing_cost
        self.vpn_cost_history.append(total_vpn_cost)
        self.cci_cost_history.append(total_cci_cost)
        recent_vpn_cost = self._recent_vpn_cost(current_hour)
        recent_cci_cost = self._recent_cci_cost(current_hour)
        if recent_cci_cost <= recent_vpn_cost:
            return CCIState.WAITING
        else:
            return CCIState.OFF

class AlwaysOnAlgorithm(DecisionAlgorithm):

    def decide(self, current_hour: int, current_state: CCIState, hours_in_state: int, total_traffic_of_previous_hour: float) -> CCIState:
        return CCIState.ON

class AlwaysOffAlgorithm(DecisionAlgorithm):

    def decide(self, current_hour: int, current_state: CCIState, hours_in_state: int, total_traffic_of_previous_hour: float) -> CCIState:
        return CCIState.OFF
