import typing as t

from bunka_logger import logger
from data_model import Individual, RawIndividual
from data_model_region import Region
from dotenv import load_dotenv
from functions_cultural_score import get_cultural_index
from functions_enrich_wikidata import (
    get_country_code,
    get_impact_years,
    raw_to_individuals,
)
from functions_manual_regions import pipeline_manual_cleaning_region_global
from functions_regions import get_individuals_regions, get_regions
from functions_wikidata import (
    get_external_identifiers,
    get_individual_main_wikidata_information,
)
from functions_wikipedia import get_wikipedia_information
from sys_utils import save_model

load_dotenv()
import os

CHECKPOINT_PATH = os.getenv("CHECKPOINT_PATH")


class Enricher:
    def __init__(self) -> None:
        pass

    def enrich(self) -> t.List[RawIndividual]:
        logger.info("Insert Wikidata Information")
        raw_individuals: t.List[RawIndividual] = (
            get_individual_main_wikidata_information()
        )
        raw_individuals: t.List[RawIndividual] = self._filter_by_date(
            raw_individuals, birthyear_max=1850
        )
        logger.info("Save Checkpoint 1")
        save_model(raw_individuals, name=CHECKPOINT_PATH + "/checkpoint_1.jsonl")

        logger.info("From RawIndividuals to Individuals")
        individuals: t.List[Individual] = raw_to_individuals(raw_individuals)

        logger.info("Get Country Code of Individuals")
        individuals: t.List[Individual] = get_country_code(individuals)

        # logger.info("Get Impact years of Individuals")
        individuals: t.List[Individual] = get_impact_years(individuals)

        logger.info("Save Checkpoint 2")
        save_model(individuals, name=CHECKPOINT_PATH + "/checkpoint_2.jsonl")

        logger.info("Insert Wikipedia Pages Information")
        individuals: t.List[Individual] = get_wikipedia_information(individuals)

        logger.info("Insert Wikidata External Identifiers")
        individuals: t.List[Individual] = get_external_identifiers(individuals)

        logger.info("Save Checkpoint 3")
        save_model(individuals, name=CHECKPOINT_PATH + "/checkpoint_3.jsonl")

        # logger.info("Compute Cultural Index of Individuals")
        # individuals: t.List[Individual] = get_cultural_index(individuals)

        # logger.info("Save Checkpoint 4")
        # save_model(individuals, name=CHECKPOINT_PATH + "checkpoint_4.jsonl")

        logger.info("Get Region Model form .csv")
        regions: t.List[Region] = get_regions()

        logger.info("Save Regions")
        save_model(regions, name=CHECKPOINT_PATH + "/regions.jsonl")

        logger.info("Get Region of Individuals")
        individuals: t.List[Individual] = get_individuals_regions(individuals, regions)

        logger.info("Save Final Individual Model with regions")
        save_model(individuals, name=CHECKPOINT_PATH + "/checkpoint_5.jsonl")

        logger.info("Correct regions manually")
        individuals: t.List[Individual] = pipeline_manual_cleaning_region_global(
            individuals
        )
        save_model(individuals, name=CHECKPOINT_PATH + "/individuals.jsonl")

        return individuals

    def _filter_by_date(
        self, individuals: t.List[RawIndividual], birthyear_max: int = 1850
    ) -> t.List[RawIndividual]:
        individuals_filter = [x for x in individuals if x.birthyear != None]
        individuals_filter = [
            x for x in individuals_filter if x.birthyear <= birthyear_max
        ]
        return individuals_filter


if __name__ == "__main__":
    enricher = Enricher()
    individuals = enricher.enrich()
