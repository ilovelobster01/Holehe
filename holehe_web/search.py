import sys
import os
import trio
import httpx
from datetime import datetime

from . import storage

# Add the holehe source to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'holehe_source')))

# Import holehe modules
try:
    from holehe.core import import_submodules, get_functions, launch_module
except ImportError:
    # This is a fallback for local development, in a real deployment
    # the holehe_source should be in the python path.
    print("Could not import holehe modules. Make sure holehe_source is in the python path.")
    # Define dummy functions to avoid crashing
    def import_submodules(path): return []
    def get_functions(modules): return []
    def launch_module(*args, **kwargs): pass


async def run_holehe_async(email, websites):
    """Run holehe async search"""
    timeout = 10
    client = httpx.AsyncClient(timeout=timeout)
    out = []

    try:
        async with trio.open_nursery() as nursery:
            for website in websites:
                nursery.start_soon(launch_module, website, email, client, out)
    finally:
        await client.aclose()

    return sorted(out, key=lambda i: i['name'])


def run_holehe_search(email, search_id):
    """Run Holehe search in background using trio"""
    try:
        storage.update_search_status(search_id, 10, 'Loading modules...')

        modules = import_submodules("holehe.modules")
        websites = get_functions(modules)

        storage.update_search_status(search_id, 20, f'Checking {len(websites)} websites...')

        results = trio.run(run_holehe_async, email, websites)

        storage.update_search_status(search_id, 90, 'Processing results...')

        # Process results
        found_profiles = []
        not_found_profiles = []
        rate_limited_profiles = []
        error_profiles = []

        for result in results:
            profile_data = {
                'site': result['name'],
                'domain': result['domain'],
                'method': result.get('method', 'unknown'),
                'emailrecovery': result.get('emailrecovery'),
                'phoneNumber': result.get('phoneNumber'),
                'others': result.get('others')
            }

            if result.get('error'):
                error_profiles.append({**profile_data, 'status': 'error', 'reason': 'Error occurred during check'})
            elif result.get('rateLimit'):
                rate_limited_profiles.append({**profile_data, 'status': 'rate_limited', 'reason': 'Rate limited'})
            elif result.get('exists'):
                found_profiles.append({**profile_data, 'status': 'found'})
            else:
                not_found_profiles.append({**profile_data, 'status': 'not_found'})

        final_results = {
            'email': email,
            'found_profiles': found_profiles,
            'not_found_profiles': not_found_profiles,
            'rate_limited_profiles': rate_limited_profiles,
            'error_profiles': error_profiles,
            'total_sites': len(websites),
            'found_count': len(found_profiles),
            'not_found_count': len(not_found_profiles),
            'rate_limited_count': len(rate_limited_profiles),
            'error_count': len(error_profiles),
            'search_time': datetime.now().isoformat()
        }

        storage.save_results(search_id, final_results)

    except Exception as e:
        storage.set_search_error(search_id, f'Error: {str(e)}')
