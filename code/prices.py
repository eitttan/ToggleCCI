import pandas as pd
from artifact_paths import PRICING_AWS_DIRECT_LINK_FILE
from defs import *
CCI_LEASING_COSTS = {'aws_gcp': 5.6 + 2.48, 'azure_gcp': 5.6 + 4.65}
GB2GiB = 1.07
df_aws_dtx = pd.read_excel(PRICING_AWS_DIRECT_LINK_FILE, index_col=0)
aws_transfer_cost = {'af-south-1': 0.147, 'ap-east-1': 0.09, 'ap-northeast-1': 0.09, 'ap-northeast-2': 0.08, 'ap-northeast-3': 0.09, 'ap-south-1': 0.086, 'ap-south-2': 0.086, 'ap-southeast-1': 0.09, 'ap-southeast-2': 0.08, 'ap-southeast-3': 0.1, 'ca-central-1': 0.02, 'eu-central-1': 0.03, 'eu-central-2': 0.03, 'eu-north-1': 0.03, 'eu-south-1': 0.03, 'eu-south-2': 0.03, 'eu-west-1': 0.03, 'eu-west-2': 0.03, 'eu-west-3': 0.03, 'me-central-1': 0.085, 'me-south-1': 0.1105, 'sa-east-1': 0.138, 'us-east-1': 0.02, 'us-east-2': 0.02, 'us-west-1': 0.02, 'us-west-2': 0.02}

def get_cci_leasing_cost(direction):
    if direction in {Direction.AWS_to_GCP, Direction.GCP_to_AWS}:
        return CCI_LEASING_COSTS['aws_gcp']
    if direction in {Direction.AZURE_to_GCP, Direction.GCP_to_AZURE}:
        return CCI_LEASING_COSTS['azure_gcp']
    raise ValueError(f'Unsupported CCI direction: {direction}')

def get_leasing_cost(edge_type, capacity, source=None, destination=None):
    leas_gcp_vlan = {1: 0.1, 2: 0.1, 5: 0.1, 10: 0.1, 20: 0.2, 50: 0.5}
    if edge_type == EdgeType.egress_google_to_cci:
        return leas_gcp_vlan[capacity]
    return 0

def get_intra_azure_traffic_price(source_cont, dest_cont):
    if source_cont == dest_cont:
        if source_cont == ContinentalName.EUROPE or source_cont == ContinentalName.NORTH_AMERICA:
            return 0.02
        if source_cont in {ContinentalName.AFRICA, ContinentalName.OCEANIA, ContinentalName.MIDDLE_EAST, ContinentalName.ASIA}:
            return 0.08
        if source_cont == ContinentalName.SOUTH_AMERICA:
            return 0.16
    if source_cont == ContinentalName.EUROPE or source_cont == ContinentalName.NORTH_AMERICA:
        return 0.05
    if source_cont in {ContinentalName.AFRICA, ContinentalName.OCEANIA, ContinentalName.MIDDLE_EAST, ContinentalName.ASIA}:
        return 0.08
    if source_cont == ContinentalName.SOUTH_AMERICA:
        return 0.16
    raise ValueError(f'Unsupported Azure continent pair: {source_cont} -> {dest_cont}')

def get_intra_google_traffic_price(source_cont, dest_cont):
    if dest_cont == ContinentalName.SOUTH_AMERICA or source_cont == ContinentalName.SOUTH_AMERICA:
        return 0.14
    if dest_cont == ContinentalName.MIDDLE_EAST or source_cont == ContinentalName.MIDDLE_EAST:
        return 0.11
    if dest_cont == ContinentalName.OCEANIA or source_cont == ContinentalName.OCEANIA:
        if dest_cont == ContinentalName.AFRICA or source_cont == ContinentalName.AFRICA:
            return 0.14
        return 0.1
    if dest_cont == ContinentalName.AFRICA or source_cont == ContinentalName.AFRICA:
        return 0.11
    if dest_cont == ContinentalName.ASIA or source_cont == ContinentalName.ASIA:
        return 0.08
    if source_cont == ContinentalName.EUROPE or source_cont == ContinentalName.NORTH_AMERICA:
        if dest_cont == source_cont:
            return 0.02
        return 0.05
    raise ValueError(f'Unsupported GCP continent pair: {source_cont} -> {dest_cont}')

def get_intra_aws_traffic_price(source_region):
    return aws_transfer_cost[source_region]

def get_inter_google_to_cci_aws_coloc_price(source_region, coloc_city):
    source_cont = get_map_region_to_continental(source_region, CloudName.GCP)
    coloc_cont = get_map_region_to_continental(coloc_city, CloudName.COLOC_AWS_GCP)
    if source_cont == ContinentalName.NORTH_AMERICA:
        return 0.02
    if coloc_cont == ContinentalName.EUROPE and source_cont == ContinentalName.EUROPE:
        return 0.02
    if coloc_cont == ContinentalName.NORTH_AMERICA and source_cont == ContinentalName.EUROPE:
        return get_intra_google_traffic_price(source_cont, coloc_cont) + 0.02
    if coloc_cont == ContinentalName.EUROPE and source_cont == ContinentalName.NORTH_AMERICA:
        return get_intra_google_traffic_price(source_cont, coloc_cont) + 0.02
    if coloc_cont == ContinentalName.MIDDLE_EAST and source_cont == ContinentalName.EUROPE:
        return 0.1
    if coloc_cont == ContinentalName.AFRICA and source_cont == ContinentalName.EUROPE:
        return 0.11
    if coloc_cont == ContinentalName.MIDDLE_EAST and source_cont == ContinentalName.MIDDLE_EAST:
        return 0.09
    if coloc_cont == ContinentalName.EUROPE and source_cont == ContinentalName.MIDDLE_EAST:
        return 0.1
    if coloc_cont == ContinentalName.AFRICA and source_cont == ContinentalName.AFRICA:
        return 0.11
    if coloc_cont == ContinentalName.ASIA:
        if coloc_city == 'Jakarta':
            if source_region == 'asia-southeast2':
                return 0.0484
            if source_cont == ContinentalName.ASIA:
                return 0.0594
        if coloc_city == 'Mumbai' and source_region in {'asia-south1', 'asia-south2'}:
            return 0.45
        if source_region == 'asia-southeast2':
            return 0.0594
        return 0.042
    if coloc_cont == ContinentalName.OCEANIA:
        return 0.042
    if coloc_cont == ContinentalName.SOUTH_AMERICA:
        if source_cont == ContinentalName.SOUTH_AMERICA:
            return 0.11
        if source_cont == ContinentalName.NORTH_AMERICA:
            return 0.1107
    raise ValueError(f'Unsupported GCP-to-colocation pair: {source_region} -> {coloc_city}')

def get_inter_aws_to_google_traffic_price(source_region, coloc_city):
    from_region = aws_regions_to_dtodx_region[source_region]
    to_region = aws_coloc_to_dtodx_region[coloc_city]
    return df_aws_dtx.at[to_region, from_region]

def get_traffic_cost(edge_type, source, destination):
    source_cont = get_map_region_to_continental(source['region'], source['cloud'])
    dest_cont = get_map_region_to_continental(destination['region'], destination['cloud'])
    traffic_cost = 1e-09
    if edge_type == EdgeType.intra_aws:
        if source['region'] == 'us-east-1' and destination['region'] == 'us-east-2' or (source['region'] == 'us-east-2' and destination['region'] == 'us-east-1'):
            traffic_cost = 0.01
        else:
            traffic_cost = get_intra_aws_traffic_price(source['region'])
    if edge_type == EdgeType.intra_azure:
        traffic_cost = get_intra_azure_traffic_price(source_cont, dest_cont)
    if edge_type == EdgeType.intra_google:
        traffic_cost = get_intra_google_traffic_price(source_cont, dest_cont)
    if edge_type == EdgeType.egress_aws_to_cci:
        traffic_cost = get_inter_aws_to_google_traffic_price(source['region'], destination['coloc_city'])
    if edge_type == EdgeType.egress_google_to_cci:
        traffic_cost = get_inter_google_to_cci_aws_coloc_price(source['region'], destination['coloc_city'])
    if edge_type == EdgeType.cci_internal:
        traffic_cost = 1e-09
    return traffic_cost
