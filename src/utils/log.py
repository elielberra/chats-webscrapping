def log_prospects_req_status(pagination_num, records_per_req):
    record_num_start = ((pagination_num + 1) * int(records_per_req)) - (int(records_per_req) - 1)
    record_num_end = (pagination_num + 1) * int(records_per_req)
    print(f'Bringing prospects: from {record_num_start} to {record_num_end}')
