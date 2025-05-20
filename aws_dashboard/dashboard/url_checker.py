import requests
def check_urls_from_file(file_path):
    results = []
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        for url in urls:
            try:
                response = requests.get(url, timeout=5)
                results.append({
                    'url': url,
                    'status': 'Healthy' if response.status_code == 200 else 'Unhealthy',
                    'status_code': response.status_code
                })
            except requests.RequestException as e:
                results.append({
                    'url': url,
                    'status': 'Error',
                    'status_code': str(e)
                })
    except FileNotFoundError:
        results.append({
            'url': f'File {file_path} not found',
            'status': 'Error',
            'status_code': 'N/A'
        })
    return results
