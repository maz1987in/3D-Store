import numpy as np

def is_null(v):
    if v is None or v == '' or v == np.nan or v == np.NaN or str(v) == 'nan' or str(v) == 'NaN':
        return True
    return False

def df_to_formatted_json(df, sep='.'):
    """
    The opstore3dite of json_normalize
    """
    #print('--------Start--------')
    result = []
    for idx, row in df.iterrows():
        #print('--------Start:ROW--------')
        parsed_row = {}
        for col_label,v in row.items():
            #print('--------Start:COL--------')
            keys = col_label.split(sep)

            current = parsed_row
            for i, k in enumerate(keys):
                if i==len(keys)-1:
                    #print('----1----')
                    if not is_null(v):
                        current[k] = v
                        #print('V is not None')
                        #print(v)
                    #else:
                    #    current[k] = None
    
                    #print(k)
                    #print(current[k])
                else:
                    #print('----2----')
                    if k not in current.keys():
                        current[k] = {}
                    current = current[k]
                    #print(k)
                    #print(current[k])
            #print('--------Start:COL--------')       
        # save
        result.append(parsed_row)
        #print('--------End:ROW--------')
    #print('--------End--------')
    return result