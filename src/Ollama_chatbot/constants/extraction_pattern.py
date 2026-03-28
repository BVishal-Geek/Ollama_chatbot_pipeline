import re

DATA_AVAILABILITY_PATTERN = [
    'Data Availability Statement', 
    'Data Availability',
    'Data availability and sharing',
    'Availability of Data and Materials',
    'Data and Code Availability',
    'Associated Data',
    'Data Accessibility',
    'Data Access',
    'Data Sharing Statement',
    'Data Sharing',
    'Availability of Supporting Data',
    'Code and Data Availability',
    'Dataset Availability',
    'Open Data Statement',
    'Public Data Availability'
]

_compiled_data_availability_pattern = [re.compile(pattern, re.IGNORECASE) for pattern in DATA_AVAILABILITY_PATTERN]

def matches_data_availability_pattern(title: str) -> bool:
    if not title:
        return False
    
    title_normalied = title.strip()
    return any(pattern.match(title_normalied) for pattern in _compiled_data_availability_pattern)
    