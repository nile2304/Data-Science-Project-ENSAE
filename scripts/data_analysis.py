def PIB_check_missing_values(data):
    return data.isna().any()
    
def reveal_missing_values(data):
    
    result = data.isna().sum()
    