import os
import random
from itertools import cycle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import ScalarFormatter
from defs import *
from prices import GB2GiB, get_cci_leasing_cost, get_inter_aws_to_google_traffic_price, get_inter_google_to_cci_aws_coloc_price
from Algorithms import *
from visualization import *

def resolve_cci_leasing_cost(settings):
    if 'cci_leasing_cost' in settings:
        return settings['cci_leasing_cost']
    return get_cci_leasing_cost(settings['direction'])

class GlobalSimulator:

    def __init__(self, hours, decision_algo, pairs, contract_hours, cci_leasing_cost):
        self.hours = hours
        self.t = 0
        self.decision_algo = decision_algo
        self.pairs = pairs
        self.global_cci_state = CCIState.OFF
        self.state_start_hour = 0
        self.total_cci_cost = 0.0
        self.cci_activation_points = []
        self.cci_decide_points = []
        self.cci_renew_points = []
        self.global_state_history = []
        self.global_cost_history = []
        self.hours_in_month = 730
        self.global_leasing_cost_history = []
        self.global_traffic_cost_history = []
        self.contract_hours = contract_hours
        self.cci_leasing_cost = cci_leasing_cost

    def isNewMonth(self):
        if self.t % self.hours_in_month == 0:
            return True
        return False

    def run(self, verbose=False):
        for t in range(self.hours):
            self.t = t
            if self.isNewMonth():
                for p in self.pairs:
                    p.monthly_vpn_GB = 0
            hours_in_state = t - self.state_start_hour
            total_traffic_prev = sum((p.trace[t - 1] for p in self.pairs)) if t > 0 else 0
            next_state = self.decision_algo.decide(current_hour=t, current_state=self.global_cci_state, hours_in_state=hours_in_state, total_traffic_of_previous_hour=total_traffic_prev)
            hour_total_cost = 0.0
            hour_traffic_cost = 0
            hour_leasing_cost = 0
            for p in self.pairs:
                traffic_t = p.trace[t - 1] if t > 0 else 0
                cost_t = traffic_t * (p.cci_rate_per_gb if self.global_cci_state == CCIState.ON else p.vpn_rate_per_gb)
                leasing_t = p.vlan_cost_per_hour if self.global_cci_state == CCIState.ON else p.vpn_cost_per_hour
                hour_total_cost += cost_t
                p.traffic_cost_history.append(cost_t)
                p.leasing_cost_history.append(leasing_t)
                if self.global_cci_state != CCIState.ON:
                    p.monthly_vpn_GB += traffic_t
                p.monthly_vpn_GB_history.append(p.monthly_vpn_GB)
                p.calculate_vpn_rate_per_gb()
                p.cost_vpn_GB_history.append(p.vpn_rate_per_gb)
                hour_leasing_cost += leasing_t
                hour_traffic_cost += cost_t
            if self.global_cci_state == CCIState.ON:
                hour_leasing_cost += self.cci_leasing_cost
            self.global_leasing_cost_history.append(hour_leasing_cost)
            self.global_traffic_cost_history.append(hour_traffic_cost)
            self.global_cost_history.append(hour_total_cost)
            self.global_state_history.append(self.global_cci_state.name)
            if next_state != self.global_cci_state:
                if verbose:
                    print(f'Hour={t}, {self.global_cci_state.name} -> {next_state.name}')
                if self.global_cci_state == CCIState.OFF and next_state == CCIState.WAITING:
                    self.cci_decide_points.append((t, next_state.value))
                if self.global_cci_state == CCIState.WAITING and next_state == CCIState.ON:
                    self.cci_activation_points.append((t, next_state.value))
                self.global_cci_state = next_state
                self.state_start_hour = t
            elif self.global_cci_state == CCIState.ON:
                if hours_in_state >= self.contract_hours:
                    self.cci_renew_points.append((t, next_state.value))

    def get_results(self):
        return {'cci_state_history': self.global_state_history, 'global_cumulative_cost_history': self.global_cost_history, 'cci_activation_points': self.cci_activation_points, 'cci_decide_points': self.cci_decide_points, 'cci_renew_points': self.cci_renew_points, 'pairs': self.pairs, 'total_cci_cost': self.total_cci_cost, 'global_leasing_cost_history': self.global_leasing_cost_history, 'global_traffic_cost_history': self.global_traffic_cost_history}

class Pair:

    def __init__(self, source, destination, trace, coloc_city):
        self.source = source
        self.destination = destination
        self.trace = trace
        self.coloc_city = coloc_city
        self.monthly_vpn_GB = 0
        self.vpn_cost_per_hour = self.calculate_vpn_cost_per_hour()
        self.vlan_cost_per_hour = 0.1
        self.cci_rate_per_gb = self.calculate_cci_rate_per_gb()
        self.vpn_rate_per_gb = self.calculate_vpn_rate_per_gb()
        self.name = f'{self.source['cloud']} : {self.source['region']} --> {self.destination['cloud']} : {self.destination['region']}'
        self.accumulated_cost = 0
        self.monthly_vpn_GB_history = []
        self.cost_vpn_GB_history = []
        self.traffic_cost_history = []
        self.leasing_cost_history = []

    def calculate_vpn_cost_per_hour(self):
        res = 0
        source = self.source
        destination = self.destination
        if source['cloud'] == CloudName.GCP or destination['cloud'] == CloudName.GCP:
            res = res + 0.05
        if source['cloud'] == CloudName.AWS or destination['cloud'] == CloudName.AWS:
            res = res + 0.05
        if source['cloud'] == CloudName.AZURE or destination['cloud'] == CloudName.AZURE:
            res = res + 0.19
        return res

    def calculate_vpn_rate_per_gb(self):
        source = self.source
        destination = self.destination
        if source['cloud'] == CloudName.GCP:
            res = 0.12
            if self.monthly_vpn_GB < GB2GiB:
                if get_map_region_to_continental(source['region'], cloud=CloudName.GCP) == ContinentalName.NORTH_AMERICA:
                    res = 0.12
                if self.monthly_vpn_GB > 1024 * GB2GiB:
                    res = 0.11
                    if self.monthly_vpn_GB > 10240 * GB2GiB:
                        res = 0.08
            res = res / GB2GiB
        if source['cloud'] == CloudName.AWS:
            res = 0.09
            if self.monthly_vpn_GB > 100:
                res = 0.09
                if self.monthly_vpn_GB > 10000:
                    res = 0.085
                    if self.monthly_vpn_GB > 50000:
                        res = 0.07
                        if self.monthly_vpn_GB > 150000:
                            res = 0.05
        if source['cloud'] == CloudName.AZURE:
            res = 0.087
            if self.monthly_vpn_GB > 100:
                res = 0.087
                if self.monthly_vpn_GB > 10000:
                    res = 0.083
                    if self.monthly_vpn_GB > 50000:
                        res = 0.07
                        if self.monthly_vpn_GB > 150000:
                            res = 0.05
        self.vpn_rate_per_gb = res
        return res

    def calculate_cci_rate_per_gb(self):
        """
        Calculates the CCI rate per GB for a pair during initialization.
        """
        coloc_city = self.coloc_city
        source_cloud = self.source['cloud']
        if source_cloud == CloudName.GCP:
            res = get_inter_google_to_cci_aws_coloc_price(source_region=self.source['region'], coloc_city=coloc_city)
            res = res / GB2GiB
        elif source_cloud == CloudName.AWS:
            res = get_inter_aws_to_google_traffic_price(source_region=self.source['region'], coloc_city=coloc_city)
        elif source_cloud == CloudName.AZURE:
            res = 0.025
        else:
            raise ValueError(f'Unsupported cloud type: {source_cloud}')
        self.cci_rate_per_gb = res
        return res

    def update_vpn_monthly(self, valGb):
        self.monthly_vpn_GB += valGb

def get_trace(length, distribution, max_vol, mean_vol):
    """
    Generates a traffic trace based on the specified distribution.

    :param length: Length of the trace (number of time units).
    :param distribution: Distribution type ("uniform", "poisson", "normal", etc.).
    :param max_vol: Maximum traffic volume (used for capping values).
    :param mean_vol: Mean traffic volume (used for distributions).
    :return: List representing the generated traffic trace.
    """
    if distribution == 'uniform':
        trace = np.random.uniform(0, max_vol, length)
    if distribution == 'constant':
        trace = np.ones(length) * mean_vol
    elif distribution == 'poisson':
        trace = np.random.poisson(mean_vol, length)
    elif distribution == 'normal':
        trace = np.random.normal(mean_vol, mean_vol / 2, length)
        trace = np.clip(trace, 0, max_vol)
    elif distribution == 'exponential':
        trace = np.random.exponential(mean_vol, length)
        trace = np.clip(trace, 0, max_vol)
    else:
        raise ValueError(f'Unsupported distribution type: {distribution}')
    return trace.tolist()

class RegionPairSelector:

    def __init__(self, num_of_gcp=6, num_of_aws=6, num_pairs=6, geography_limited=False, continental=None, gcp_continents=None, aws_continents=None, coloc_city=None):
        """
        Initializes the region pair selection based on AWS and GCP colocations.
        :param num_of_gcp: Number of GCP regions to select
        :param num_of_aws: Number of AWS regions to select
        :param geography_limited: If True, limit pairs to the same continent (geography)
        """
        self.num_of_gcp = num_of_gcp
        self.num_of_aws = num_of_aws
        self.num_pairs = num_pairs
        self.geography_limited = geography_limited
        self.continental = continental
        self.coloc_city = coloc_city
        all_aws_regions = list(continental_dict[CloudName.AWS].keys())
        all_gcp_regions = list(continental_dict[CloudName.GCP].keys())
        self.aws_geography = continental_dict[CloudName.AWS]
        self.gcp_geography = continental_dict[CloudName.GCP]
        if gcp_continents is not None or aws_continents is not None:
            gcp_continents = set(gcp_continents or continental_dict[CloudName.GCP].values())
            aws_continents = set(aws_continents or continental_dict[CloudName.AWS].values())
            self.gcp_regions = [gcp for gcp, gcp_continent in self.gcp_geography.items() if gcp_continent in gcp_continents]
            self.aws_regions = [aws for aws, aws_continent in self.aws_geography.items() if aws_continent in aws_continents]
        elif continental is None:
            self.aws_regions = all_aws_regions
            self.gcp_regions = all_gcp_regions
        else:
            self.aws_regions = [aws for aws, aws_continent in self.aws_geography.items() if aws_continent == continental]
            self.gcp_regions = [gcp for gcp, gcp_continent in self.gcp_geography.items() if gcp_continent == continental]
        self.aws_geography = continental_dict[CloudName.AWS]
        self.gcp_geography = continental_dict[CloudName.GCP]

    def _randomize_direction(self, aws, gcp):
        """
        Randomly decides the direction of the pair (AWS -> GCP or GCP -> AWS).
        :param aws: AWS region
        :param gcp: GCP region
        :return: Tuple in random order (aws, gcp) or (gcp, aws)
        """
        direction = random.choice([True, False])
        print(f'Random choice for direction: {direction}')
        if direction:
            return (aws, gcp)
        else:
            return (gcp, aws)

    def _get_same_geography_pairs(self):
        """
        Selects AWS and GCP pairs limited to the same continent.
        """
        geography_pairs = []
        for aws_region, aws_continent in self.aws_geography.items():
            gcp_regions_in_same_continent = [gcp for gcp, gcp_continent in self.gcp_geography.items() if gcp_continent == aws_continent]
            if gcp_regions_in_same_continent:
                gcp_region = random.choice(gcp_regions_in_same_continent)
                geography_pairs.append(self._randomize_direction(aws_region, gcp_region))
            if len(geography_pairs) >= min(self.num_of_aws, self.num_of_gcp):
                break
        return geography_pairs

    def _get_unrestricted_pairs(self):
        """
        Selects AWS and GCP pairs without limiting geography.
        """
        selected_aws = np.random.choice(self.aws_regions, self.num_of_aws, replace=False).tolist()
        selected_gcp = np.random.choice(self.gcp_regions, self.num_of_gcp, replace=False).tolist()
        random.shuffle(selected_aws)
        random.shuffle(selected_gcp)
        unrestricted_pairs = [self._randomize_direction(aws, gcp) for aws, gcp in zip(selected_aws, selected_gcp)]
        return unrestricted_pairs

    def get_region_pairs(self, predefine=False, direction=None):
        """
        Generates pairs with pre-computed CCI rate per GB.
        """
        ix = 0
        if predefine:
            selected_aws = ['eu-central-1', 'eu-central-2', 'eu-west-1', 'us-east-2', 'us-west-1', 'us-west-2']
            selected_gcp = ['europe-central1', 'europe-central2', 'europe-west1', 'us-central1', 'us-east1', 'us-east4']
            direction_predefine = [True, False, True, False, True, False]
        else:
            selected_aws = random.choices(self.aws_regions, k=self.num_of_aws)
            selected_gcp = random.choices(self.gcp_regions, k=self.num_of_gcp)
        pairs = []
        if self.coloc_city:
            coloc_city = self.coloc_city
        elif self.continental == ContinentalName.EUROPE:
            coloc_city = 'Paris'
        else:
            coloc_city = 'Ohio'
        selected_aws = random.choices(selected_aws, k=self.num_pairs)
        selected_gcp = random.choices(selected_gcp, k=self.num_pairs)
        while ix < self.num_pairs:
            aws = selected_aws[ix]
            if predefine:
                gcp = selected_gcp[ix]
                if direction_predefine[ix]:
                    source = {'region': aws, 'cloud': CloudName.AWS}
                    destination = {'region': gcp, 'cloud': CloudName.GCP}
                else:
                    source = {'region': gcp, 'cloud': CloudName.GCP}
                    destination = {'region': aws, 'cloud': CloudName.AWS}
            else:
                gcp = selected_gcp[ix]
                if direction == Direction.GCP_to_AZURE:
                    source = {'region': gcp, 'cloud': CloudName.GCP}
                    destination = {'region': aws, 'cloud': CloudName.AZURE}
                elif direction == Direction.AZURE_to_GCP:
                    source = {'region': aws, 'cloud': CloudName.AZURE}
                    destination = {'region': gcp, 'cloud': CloudName.GCP}
                elif (random.choice([True, False]) or direction == Direction.AWS_to_GCP) and direction != Direction.GCP_to_AWS:
                    source = {'region': aws, 'cloud': CloudName.AWS}
                    destination = {'region': gcp, 'cloud': CloudName.GCP}
                else:
                    source = {'region': gcp, 'cloud': CloudName.GCP}
                    destination = {'region': aws, 'cloud': CloudName.AWS}
            ix = ix + 1
            p = Pair(source=source, destination=destination, trace=[], coloc_city=coloc_city)
            pairs.append(p)
        return pairs

def get_trace_poisson_process(length, lambda_interval, duration_mean, intensity_mean, intensity_std):
    """
    Generates a traffic trace based on a Poisson process where bursts of traffic occur.

    :param length: Total duration of the trace (number of time units).
    :param lambda_interval: Rate of Poisson process (average interval between bursts).
    :param duration_mean: Mean duration of each burst (K).
    :param intensity_mean: Mean intensity (V) of the burst.
    :param intensity_std: Standard deviation of intensity.
    :return: List representing the generated traffic trace.
    """
    trace = np.zeros(length)
    current_time = 0
    while current_time < length:
        time_to_next_burst = np.random.exponential(1 / lambda_interval)
        current_time += int(time_to_next_burst)
        if current_time >= length:
            break
        burst_duration = np.abs(int(np.random.normal(duration_mean, duration_mean / 2)))
        burst_duration = min(burst_duration, length - current_time)
        burst_intensity = max(0, np.random.normal(intensity_mean, intensity_std))
        trace[current_time:current_time + burst_duration] += burst_intensity
        current_time += burst_duration
    return trace.tolist()

def read_csv_folder(folder_path, save_path=None, load_existing=True):
    """
    Reads all CSV files in a folder, sums data hourly, and optionally saves/loads the processed table.

    Parameters:
    - folder_path (str): Path to the folder containing CSV files.
    - save_path (str, optional): File path to save/load the processed data as a CSV.
    - load_existing (bool, optional): If True, loads processed data from `save_path` if it exists.

    Returns:
    - pd.DataFrame: A DataFrame containing the processed hourly data.
    """
    if os.path.isfile(folder_path):
        print(f'Loading preprocessed trace from {folder_path}')
        return pd.read_csv(folder_path, index_col=0)
    if save_path and load_existing and os.path.isfile(save_path):
        print(f'Loading existing processed data from {save_path}')
        return pd.read_csv(save_path, index_col=0)
    files = sorted([f for f in os.listdir(folder_path) if f.endswith('.csv')])
    hourly_summed_data = []
    for file in files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path, header=None)
        if df.shape != (1440, 7):
            print(f'Skipping {file} due to unexpected dimensions: {df.shape}')
            continue
        hourly_sums = df.groupby(df.index // 60).sum()
        hourly_summed_data.append(hourly_sums)
    if not hourly_summed_data:
        print('No valid data processed.')
        return None
    result_df = pd.concat(hourly_summed_data, ignore_index=True)
    if save_path:
        result_df.to_csv(save_path)
        print(f'Processed data saved to {save_path}')
    return result_df

def compare_algorithms(settings, mean_traffic=10, seed=10):
    random.seed(seed)
    np.random.seed(seed)
    cci_leasing_cost = resolve_cci_leasing_cost(settings)
    num_of_pairs = settings['num_of_pairs']
    HOURS = settings['HOURS']
    CONTINENTAL = settings['CONTINENTAL']
    direction = settings['direction']
    region_selector = RegionPairSelector(num_of_gcp=num_of_pairs, num_of_aws=num_of_pairs, num_pairs=num_of_pairs, geography_limited=False, continental=CONTINENTAL, gcp_continents=settings.get('gcp_continents'), aws_continents=settings.get('aws_continents'), coloc_city=settings.get('coloc_city'))
    pairs_data = region_selector.get_region_pairs(predefine=False, direction=direction)
    trace_from_file = settings['trace_from_file']
    toPlot = settings['toPlot']
    dist = settings['dist']
    total_traffic_actual = 0
    if trace_from_file:
        folder_path = settings['file']
        columns_data = read_csv_folder(folder_path, folder_path, True)
        if 'mirage' in settings['file']:
            columns_data = mean_traffic * columns_data / 1000000000.0
        if 'puffer' in settings['file']:
            columns_data = mean_traffic * columns_data
        ix_start = 0
        ix_end = ix_start + HOURS
        columns_data = columns_data.iloc[ix_start:ix_end].reset_index(drop=True)
        cols = columns_data.columns.to_list()
        np.random.shuffle(cols)
        split_columns = np.array_split(cols, num_of_pairs)
    for i, p in enumerate(pairs_data):
        if trace_from_file:
            traffic_list = columns_data[split_columns[i]].sum(axis=1)
        elif dist == 'poisson':
            mean_traffic = settings['poisson_mean_intense']
            traffic_list = get_trace_poisson_process(length=HOURS, lambda_interval=settings['lambda_interval'], duration_mean=settings['duration_mean'], intensity_mean=mean_traffic * np.random.uniform(1, 1, size=1), intensity_std=mean_traffic * 0.5)
        else:
            traffic_list = get_trace(length=HOURS, distribution=dist, max_vol=200, mean_vol=mean_traffic)
        p.trace = traffic_list
        total_traffic_actual += sum(traffic_list)
    available_algorithms = {'VPN': lambda: AlwaysOffAlgorithm(), 'CCI': lambda: AlwaysOnAlgorithm(), paper_algo_name: lambda: SkiRentalLikeAlgorithm(settings['contract_hours'], settings['ski_rental_history'], settings['c1'], settings['c2'], settings['delay_hours'], cci_leasing_cost), monthly_algo_name: lambda: SkiRentalLikeAlgorithm(settings['contract_hours'], 730, 1, 1, settings['delay_hours'], cci_leasing_cost), all_history_algo_name: lambda: SkiRentalLikeAlgorithm(settings['contract_hours'], settings['HOURS'], 1, 1, settings['delay_hours'], cci_leasing_cost), 'Oracle': lambda: OracleAlgorithm(pairs=pairs_data, hours=HOURS, k=168)}
    selected_algo_names = settings['algorithm_names']
    algorithms = {name: available_algorithms[name]() for name in selected_algo_names if name in available_algorithms}
    total_costs = {}
    leasing_costs = {}
    traffic_costs = {}
    hourly_cumulative_costs = {algo_name: [0] * HOURS for algo_name in algorithms}
    total_results = {algo_name: {} for algo_name in algorithms}
    for name, algo in algorithms.items():
        for p in pairs_data:
            p.monthly_vpn_GB = 0
            p.cost_vpn_GB_history = []
            p.monthly_vpn_GB_history = []
            p.calculate_cci_rate_per_gb()
            p.calculate_vpn_rate_per_gb()
            p.traffic_cost_history = []
            p.leasing_cost_history = []
        if name in {'SkiRentalLikeSmartVPN', paper_algo_name, monthly_algo_name, all_history_algo_name}:
            algo.set_pairs(pairs_data)
        total_leasing = 0
        total_traffic = 0
        print(f'Running simulation for algorithm: {name}')
        sim = GlobalSimulator(hours=HOURS, decision_algo=algo, pairs=pairs_data, contract_hours=settings['contract_hours'], cci_leasing_cost=cci_leasing_cost)
        sim.run()
        results = sim.get_results()
        total_results[name] = results
        hours_range = list(range(HOURS))
        hourly_traffic = [sum((p.trace[t] for p in results['pairs'])) for t in hours_range]
        cci_state_encoded = [0 if state == 'OFF' else 1 if state == 'WAITING' else 2 for state in results['cci_state_history']]
        leasing_costs[name] = sum(results['global_leasing_cost_history'])
        traffic_costs[name] = sum(results['global_traffic_cost_history'])
        total_costs[name] = leasing_costs[name] + traffic_costs[name]
        hourly_cumulative_costs[name] = np.cumsum(np.array(results['global_traffic_cost_history']) + np.array(results['global_leasing_cost_history']))
        if (toPlot and settings['PlotToPaper']) and name == paper_algo_name:
            plot_traffic_state_cost2(results, hours_range, hourly_traffic, cci_state_encoded, hourly_cumulative_costs[name], algo.cci_thresh_log, algo.vpn_thresh_log, algo.vpn_cost_history, algo.cci_cost_history, algorithm_name=name)
        if (toPlot and settings['PlotToPaper']) and name == monthly_algo_name:
            plot_debug_monthly(results, hours_range, hourly_traffic, cci_state_encoded, hourly_cumulative_costs[name], algo.vpn_cost_history, algo.cci_cost_history, algorithm_name=name)
        if (toPlot and settings['PlotToPaper']) and name in ['Oracle'] and True:
            plot_traffic_state_cost2(results, hours_range, hourly_traffic, cci_state_encoded, hourly_cumulative_costs[name], algo.activation_hours, algo.activation_hours, algo.activation_hours, algo.activation_hours, algorithm_name=name)
        if toPlot and name == 'VPN' and False:
            for p in sim.pairs:
                plot_pair_vpn_monthly(p, name)
    if toPlot:
        plot_effective_cost_per_GB(hourly_cumulative_costs, hourly_traffic, HOURS)
        plot_cost_breakdown(leasing_costs, traffic_costs)
    return (total_costs, total_traffic_actual)

def compare_algorithms_with_breakdown(settings, mean_traffic=10, seed=10):
    settings = dict(settings)
    settings['toPlot'] = False
    total_costs, total_traffic_actual = compare_algorithms(settings, mean_traffic, seed)
    breakdown = {}
    random.seed(seed)
    np.random.seed(seed)
    cci_leasing_cost = resolve_cci_leasing_cost(settings)
    num_of_pairs = settings['num_of_pairs']
    HOURS = settings['HOURS']
    region_selector = RegionPairSelector(num_of_gcp=num_of_pairs, num_of_aws=num_of_pairs, num_pairs=num_of_pairs, geography_limited=False, continental=settings['CONTINENTAL'], gcp_continents=settings.get('gcp_continents'), aws_continents=settings.get('aws_continents'), coloc_city=settings.get('coloc_city'))
    pairs_data = region_selector.get_region_pairs(predefine=False, direction=settings['direction'])
    if settings['trace_from_file']:
        columns_data = read_csv_folder(settings['file'], settings['file'], True)
        if 'mirage' in settings['file']:
            columns_data = mean_traffic * columns_data / 1000000000.0
        if 'puffer' in settings['file']:
            columns_data = mean_traffic * columns_data
        columns_data = columns_data.iloc[:HOURS].reset_index(drop=True)
        cols = columns_data.columns.to_list()
        np.random.shuffle(cols)
        split_columns = np.array_split(cols, num_of_pairs)
    for i, pair in enumerate(pairs_data):
        if settings['trace_from_file']:
            pair.trace = columns_data[split_columns[i]].sum(axis=1)
        elif settings['dist'] == 'poisson':
            pair.trace = get_trace_poisson_process(length=HOURS, lambda_interval=settings['lambda_interval'], duration_mean=settings['duration_mean'], intensity_mean=settings['poisson_mean_intense'] * np.random.uniform(1, 1, size=1), intensity_std=settings['poisson_mean_intense'] * 0.5)
        else:
            pair.trace = get_trace(length=HOURS, distribution=settings['dist'], max_vol=200, mean_vol=mean_traffic)
    available_algorithms = {'VPN': lambda: AlwaysOffAlgorithm(), 'CCI': lambda: AlwaysOnAlgorithm(), paper_algo_name: lambda: SkiRentalLikeAlgorithm(settings['contract_hours'], settings['ski_rental_history'], settings['c1'], settings['c2'], settings['delay_hours'], cci_leasing_cost), monthly_algo_name: lambda: SkiRentalLikeAlgorithm(settings['contract_hours'], 730, 1, 1, settings['delay_hours'], cci_leasing_cost), all_history_algo_name: lambda: SkiRentalLikeAlgorithm(settings['contract_hours'], settings['HOURS'], 1, 1, settings['delay_hours'], cci_leasing_cost)}
    algorithms = {name: available_algorithms[name]() for name in settings['algorithm_names'] if name in available_algorithms}
    for name, algo in algorithms.items():
        for pair in pairs_data:
            pair.monthly_vpn_GB = 0
            pair.cost_vpn_GB_history = []
            pair.monthly_vpn_GB_history = []
            pair.calculate_cci_rate_per_gb()
            pair.calculate_vpn_rate_per_gb()
            pair.traffic_cost_history = []
            pair.leasing_cost_history = []
        if name in {paper_algo_name, monthly_algo_name, all_history_algo_name}:
            algo.set_pairs(pairs_data)
        sim = GlobalSimulator(hours=HOURS, decision_algo=algo, pairs=pairs_data, contract_hours=settings['contract_hours'], cci_leasing_cost=cci_leasing_cost)
        sim.run()
        results = sim.get_results()
        leasing_cost = sum(results['global_leasing_cost_history'])
        traffic_cost = sum(results['global_traffic_cost_history'])
        breakdown[name] = {'leasing_cost': float(leasing_cost), 'traffic_cost': float(traffic_cost), 'total_cost': float(leasing_cost + traffic_cost)}
    return (breakdown, total_costs, total_traffic_actual)

def run_simulations_with_general_sweeping(settings):
    seed = settings['seed']
    random.seed(seed)
    np.random.seed(seed)
    param_name = settings['param_to_sweep']
    sweep_values = settings['sweep_values']
    algorithm_names = settings['algorithm_names']
    num_repeats = settings.get('num_repeats', 10)
    total_cost_summary = {algo: [] for algo in algorithm_names}
    mean_traffic_values_actual = {}
    for param_value in sweep_values:
        print(f'\nRunning simulations for {param_name}: {param_value}')
        settings[param_name] = param_value
        cost_accumulator = {algo: [] for algo in algorithm_names}
        param_actual_values_curr = []
        for ind in range(num_repeats):
            total_costs, total_traffic = compare_algorithms(settings, settings['mean_traffic'], seed + ind)
            for algo in algorithm_names:
                cost_accumulator[algo].append(total_costs.get(algo, 0))
        linestyles = cycle(['-', '--', '-.', ':'])
        markers = cycle(['o', 's', 'D', '^', 'v', '<', '>', 'x', '*', '+', 'p', 'h'])
        for algo in algorithm_names:
            avg_cost = np.mean(cost_accumulator[algo])
            total_cost_summary[algo].append(avg_cost)
        if settings['toPlot']:
            plt.figure(figsize=(8, 6))
            for algo in algorithm_names:
                plt.plot(range(num_repeats), cost_accumulator[algo], linestyle=next(linestyles), marker=next(markers), label=algo)
            plt.xlabel('Repeat #')
            plt.ylabel('Total Cost [USD]')
            plt.title(f'Total Cost per Run for {param_name}={param_value}')
            plt.legend()
            plt.grid()
            if settings['output_dir']:
                plt.savefig(os.path.join(settings['output_dir'], f'costs_{param_name}_{param_value}.png'))
    linestyles = cycle(['-', '--', '-.', ':'])
    markers = cycle(['o', 's', 'D', '^', 'v', '<', '>', 'x', '*', '+', 'p', 'h'])
    x_vals = sweep_values
    plt.figure(figsize=(6, 4))
    for algo in algorithm_names:
        y_vals = total_cost_summary[algo]
        plt.plot(x_vals, y_vals, linestyle=next(linestyles), marker=next(markers), label=algo)
    xlabel = settings['xlabel_sweep']
    plt.xlabel(xlabel, fontsize=18)
    plt.ylabel('Total Cost [USD]', fontsize=18)
    if not settings.get('PlotToPaper', False):
        plt.title(f'Total Cost vs {param_name.capitalize()} for Different Algorithms')
    plt.legend(fontsize=14)
    plt.grid()
    plt.yticks(fontsize=18)
    plt.xticks(fontsize=18)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax.yaxis.get_offset_text().set_fontsize(18)
    plt.xticks(fontsize=18)
    plt.tight_layout()
    if settings['output_dir']:
        plt.savefig(os.path.join(settings['output_dir'], f'summary_{param_name}.png'))
        plt.savefig(os.path.join(settings['output_dir'], f'summary_{param_name}.pdf'), format='pdf', dpi=300)
    return (total_cost_summary, total_traffic)
