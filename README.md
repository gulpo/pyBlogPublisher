# PyNewsPublisher

## Idea

Create a tool that will:
1. Read Notion database of recommended articles.
2. Format articles into markdown divided by categories thus creating news article
3. Publish news article to Confluence at specified place
4. Communicate new news&techies issue

Most probably this publisher will be strictly tailor for my Notion database so.. You have been warned

### Communication with Notion

Through Notion API. Python libraries are either too complex for simple case as this.

### Communication with Confluence

TODO

### communication with RocketChat/Teams/Mail

TODO

## Installation

1. install python 3.12.0
I'm not using any advanced tools so probably any v3 python is enough
2. Clone git repository

## Configuration

### Notion

Create Notion integration
Enable integration in Notion database of choice
Required items from Notion:
- integration secret - notion_secret
- database id - notion_database_id

## TODO

- read Notion credentials from env variables
- Confluence integration
- Teams/RocketChat integration
- Mail integration? Like mail to d.ozog to communicate new issue to wider audience?
