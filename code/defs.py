from enum import Enum
paper_algo_name = 'ToggleCCI'
monthly_algo_name = 'Avg (Month)'
all_history_algo_name = 'Avg (All)'

class CCIState(Enum):
    OFF = 1
    WAITING = 2
    ON = 3

class EdgeType(Enum):
    zero_cost = 0
    intra_aws = 1
    intra_azure = 2
    intra_google = 3
    egress_aws_to_cci = 4
    ingress_cci_to_google = 5
    egress_google_to_cci = 6
    ingress_cci_to_aws = 7
    cci_internal = 8

class ContinentalName(Enum):
    NORTH_AMERICA = 1
    EUROPE = 2
    SOUTH_AMERICA = 3
    ASIA = 4
    OCEANIA = 5
    MIDDLE_EAST = 6
    AFRICA = 7

class CloudName(Enum):
    AWS = 1
    GCP = 2
    AZURE = 3
    COLOC_AWS_GCP = 4
    COLOC_AZURE_GCP = 5

class Direction(Enum):
    AWS_to_GCP = 1
    GCP_to_AWS = 2
    AZURE_to_GCP = 3
    GCP_to_AZURE = 4
continental_dict = {}
continental_dict[CloudName.GCP] = {'us-central1': ContinentalName.NORTH_AMERICA, 'us-east1': ContinentalName.NORTH_AMERICA, 'us-east4': ContinentalName.NORTH_AMERICA, 'us-east5': ContinentalName.NORTH_AMERICA, 'us-west1': ContinentalName.NORTH_AMERICA, 'us-west2': ContinentalName.NORTH_AMERICA, 'us-west3': ContinentalName.NORTH_AMERICA, 'us-west4': ContinentalName.NORTH_AMERICA, 'us-south1': ContinentalName.NORTH_AMERICA, 'northamerica-northeast1': ContinentalName.NORTH_AMERICA, 'northamerica-northeast2': ContinentalName.NORTH_AMERICA, 'southamerica-east1': ContinentalName.SOUTH_AMERICA, 'southamerica-west1': ContinentalName.SOUTH_AMERICA, 'southamerica-east2': ContinentalName.SOUTH_AMERICA, 'europe-north1': ContinentalName.EUROPE, 'europe-southwest1': ContinentalName.EUROPE, 'europe-central1': ContinentalName.EUROPE, 'europe-central2': ContinentalName.EUROPE, 'europe-west1': ContinentalName.EUROPE, 'europe-west2': ContinentalName.EUROPE, 'europe-west3': ContinentalName.EUROPE, 'europe-west4': ContinentalName.EUROPE, 'europe-west5': ContinentalName.EUROPE, 'europe-west6': ContinentalName.EUROPE, 'europe-west7': ContinentalName.EUROPE, 'europe-west8': ContinentalName.EUROPE, 'europe-west9': ContinentalName.EUROPE, 'europe-west10': ContinentalName.EUROPE, 'europe-west12': ContinentalName.EUROPE, 'asia-east1': ContinentalName.ASIA, 'asia-east2': ContinentalName.ASIA, 'asia-northeast1': ContinentalName.ASIA, 'asia-northeast2': ContinentalName.ASIA, 'asia-northeast3': ContinentalName.ASIA, 'asia-south1': ContinentalName.ASIA, 'asia-south2': ContinentalName.ASIA, 'asia-southeast1': ContinentalName.ASIA, 'asia-southeast2': ContinentalName.ASIA, 'australia-southeast1': ContinentalName.OCEANIA, 'australia-southeast2': ContinentalName.OCEANIA, 'me-central1': ContinentalName.MIDDLE_EAST, 'me-central2': ContinentalName.MIDDLE_EAST, 'me-west1': ContinentalName.MIDDLE_EAST}
continental_dict[CloudName.AWS] = {'af-south-1': ContinentalName.AFRICA, 'ap-east-1': ContinentalName.ASIA, 'ap-northeast-1': ContinentalName.ASIA, 'ap-northeast-2': ContinentalName.ASIA, 'ap-northeast-3': ContinentalName.ASIA, 'ap-south-1': ContinentalName.ASIA, 'ap-south-2': ContinentalName.ASIA, 'ap-southeast-1': ContinentalName.ASIA, 'ap-southeast-2': ContinentalName.ASIA, 'ap-southeast-3': ContinentalName.ASIA, 'ca-central-1': ContinentalName.NORTH_AMERICA, 'eu-central-1': ContinentalName.EUROPE, 'eu-central-2': ContinentalName.EUROPE, 'eu-north-1': ContinentalName.EUROPE, 'eu-south-1': ContinentalName.EUROPE, 'eu-south-2': ContinentalName.EUROPE, 'eu-west-1': ContinentalName.EUROPE, 'eu-west-2': ContinentalName.EUROPE, 'eu-west-3': ContinentalName.EUROPE, 'me-central-1': ContinentalName.MIDDLE_EAST, 'me-south-1': ContinentalName.MIDDLE_EAST, 'sa-east-1': ContinentalName.SOUTH_AMERICA, 'us-east-1': ContinentalName.NORTH_AMERICA, 'us-east-2': ContinentalName.NORTH_AMERICA, 'us-west-1': ContinentalName.NORTH_AMERICA, 'us-west-2': ContinentalName.NORTH_AMERICA}
continental_dict[CloudName.COLOC_AWS_GCP] = {'cdg-zone1-1536': ContinentalName.EUROPE, 'cdg-zone2-1536': ContinentalName.EUROPE, 'Paris': ContinentalName.EUROPE, 'Ohio': ContinentalName.NORTH_AMERICA}
aws_regions_to_dtodx_region = {'af-south-1': 'Africa (Cape Town, Lagos)', 'ap-east-1': 'Asia Pacific (Seoul, Singapore, Hong Kong, Bangkok)', 'ap-northeast-1': 'Asia Pacific (Tokyo, Osaka)', 'ap-northeast-2': 'Asia Pacific (Seoul, Singapore, Hong Kong, Bangkok)', 'ap-northeast-3': 'Asia Pacific (Tokyo, Osaka)', 'ap-south-1': 'Asia Pacific (India)', 'ap-south-2': 'Asia Pacific (India)', 'ap-southeast-1': 'Asia Pacific (Seoul, Singapore, Hong Kong, Bangkok)', 'ap-southeast-2': 'Asia Pacific (Australia, Auckland)', 'ap-southeast-3': 'Asia Pacific (Indonesia)', 'ca-central-1': 'Canada', 'eu-central-1': 'Europe', 'eu-central-2': 'Europe', 'eu-north-1': 'Europe', 'eu-south-1': 'Europe', 'eu-south-2': 'Europe', 'eu-west-1': 'Europe', 'eu-west-2': 'Europe', 'eu-west-3': 'Europe', 'me-central-1': 'Middle East', 'me-south-1': 'Middle East', 'sa-east-1': 'South America (Sao Paulo, Mexico)', 'us-east-1': 'Contiguous United States*', 'us-east-2': 'Contiguous United States*', 'us-west-1': 'Contiguous United States*', 'us-west-2': 'Contiguous United States*'}
aws_coloc_to_dtodx_region = {'Hong Kong': 'Hong Kong SAR, Malaysia, S. Korea, Singapore & Taiwan, Bangkok', 'Jakarta': 'Indonesia ', 'Osaka': 'Japan', 'Seoul': 'Hong Kong SAR, Malaysia, S. Korea, Singapore & Taiwan, Bangkok', 'Singapore': 'Hong Kong SAR, Malaysia, S. Korea, Singapore & Taiwan, Bangkok', 'Tokyo': 'Japan', 'Sydney': 'Australia, New Zealand', 'Frankfurt': 'Europe', 'London': 'Europe', 'Madrid': 'Europe', 'Paris': 'Europe', 'Stockholm': 'Europe', 'Mumbai': 'India', 'Washington D.C.': 'Contiguous United States', 'Ohio': 'Contiguous United States', 'Dallas, Texas': 'Contiguous United States', 'Montréal': 'Canada', 'Portland, Oregon': 'Contiguous United States', 'San Francisco': 'Contiguous United States', 'Seattle': 'Contiguous United States', 'São Paulo': 'South America,  Mexico'}
map_continental_to_azure_direct_zone = {ContinentalName.NORTH_AMERICA: 1, ContinentalName.SOUTH_AMERICA: 3, ContinentalName.EUROPE: 1, ContinentalName.AFRICA: 3, ContinentalName.ASIA: 2, ContinentalName.MIDDLE_EAST: 2, ContinentalName.OCEANIA: 1}

def get_map_continental_to_azure_direct_zone(city):
    return map_continental_to_azure_direct_zone[continental_dict[city]]

def get_map_city_to_continental(city):
    return continental_dict[city]

def get_map_region_to_continental(region, cloud):
    return continental_dict[cloud][region]
