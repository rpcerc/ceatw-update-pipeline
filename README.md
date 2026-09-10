# Computing Education Around the World: Update Pipeline
The update pipeline backend for the Computing Education Around The World (CEATW) project, written in Python with Gemini and Exa AI used for scraping.

Here how the update pipeline fits in with the rest of the CEATW project:
1. The pipeline gathers a list of potential curricular sources and adds them to a *source decision* database (hosted on Neon)
2. RPCERC members then use the *human vetting app* to make a *decision* on a country's computing curriculum, based on the sources gathered by the pipeline. 
3. These decisions are then used to automatically update the curricular [dataset](https://github.com/rpcerc/ceatw-dataset) and map.

The pipeline automatically runs once a month using the GitHub Actions script in [`.github/workflows/gather-potential-sources.yaml`](.github/workflows/gather-potential-sources.yaml), which runs [`src/ceatw_update_pipeline/main.py`](src/ceatw_update_pipeline/main.py).

## Maintaining

### Repository Breakdown
Here's a more detailed breakdown of the how the update pipeline works. Make sure you're familiar with these files before making changes:
1. Gather a set of potential curricular sources for each country (`insert_urls_for_one_country` in [`main.py`](src/ceatw_update_pipeline/main.py))
   - This uses Exa AI and Gemini (for translating prompts into the native language of the country. Sometimes this finds sources that an English prompt doesn't.), which are called using the scripts in [`gather_sources.py`](src/ceatw_update_pipeline/gather_sources.py).
2. For each source that doesn't already exist in the sources database, add it to the sources database (using the `insert_source_and_highlights` in [`main.py`](src/ceatw_update_pipeline/main.py)).
   - This makes use of the Python files in the [`database/`](src/ceatw_update_pipeline/database/) directory, with the DB's representation of a source modelled in [`models.py`](src/ceatw_update_pipeline/database/models.py).

There are several other important functions/types in the [`database/`](src/ceatw_update_pipeline/database/) directory which are responsible for interactions with the Neon DB. [`database.py`](src/ceatw_update_pipeline/database/database.py) manages the session used to insert sources/highlights into the tables, while [`query.py`](src/ceatw_update_pipeline/database/query.py) is where the actual queries are run.

### Local Development
To run this pipeline locally, you'll need the following in your `.env` file:
- API keys for Gemini and Exa AI
- A connection string for the Neon database.

You can make your own version of these for free (we've capped number of Exa queries we're making per second so you shouldn't exceed free limits,). See the [`.env.example`](.env.example) for formatting your `.env` file.

Once you've done this, setup the venv and then run `pip install -e`. Run the pipeline by running [`python src/ceatw_update_pipeline/main.py`](src/ceatw_update_pipeline/main.py).

## Contributing
Improvements and error fixes are welcome. However, in order for us to incorporate your changes, we suggest you contact us before making a pull request. Alternatively, you can open up an [issue](https://github.com/rpcerc/ceatw-update-pipeline/tree/development) if you notice something wrong.