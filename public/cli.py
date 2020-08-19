import json
import logging
import click
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from social_network.domain_models import Base
from social_network.settings import DATABASE
from social_network.settings import Config


@click.group()
def cli(): pass


@cli.command()
def init_database():
    url = URL(
        DATABASE["DRIVER"],
        DATABASE["USER"],
        DATABASE["PASSWORD"],
        DATABASE["HOST"],
        None,
        DATABASE["NAME"]
    )
    engine = create_engine(url)
    Base.metadata.create_all(engine)



if __name__ == "__main__":
    with open(Config.LOGGING_SETTINGS, "r") as f:
        logging.config.dictConfig(json.load(f))
    cli()
