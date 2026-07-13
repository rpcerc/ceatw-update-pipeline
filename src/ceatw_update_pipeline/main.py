from ceatw_update_pipeline.gather_sources import get_exa_sources
from dotenv import load_dotenv

from ceatw_update_pipeline.filter_source import contains_computing_curriculum

if __name__ == "__main__":
    load_dotenv()
    for source in get_exa_sources("Angola"):
        if (contains_computing_curriculum(source)):
            print("Maybe a good link")
        else:
            print("Probably a bad link")
        print(source["url"])
        print("---------------------------- -------------------------------")