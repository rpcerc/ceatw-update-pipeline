"""Custom tests that shouldn't be caught with pytest."""

import asyncio

from ceatw_update_pipeline.main import load_native_prompts_cache
from ceatw_update_pipeline.gather_sources import get_exa_sources

def test():
    sources = asyncio.run(get_exa_sources("DE", load_native_prompts_cache()))
    
    for source in sources:
        print(source.highlights)
        print("WAH-------------------------------------\n\n")
    
if __name__ == "__main__":
    test()