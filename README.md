# PyNewsPublisher

## Idea

Create a tool that will:
1. Read Notion database of recommended articles.
2. Format articles into markdown divided by categories thus creating news article
    [Markdown syntax](https://www.markdownguide.org/basic-syntax/)
3. Publish news article to Confluence at specified place
    Confluence should understand markdown with [the plugin](https://marketplace.atlassian.com/apps/1211438/markdown-macro-html-plantuml-latex-diagrams-open-api?hosting=server&tab=overview)
4. Communicate new news&techies issue in interactive medium of choice

Most probably this publisher will be strictly tailored for my Notion database so.. You have been warned


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
3. use editorconfig plugin to help format files correctly

## Configuration

### Notion

Create Notion integration
Enable integration in Notion database of choice
Required items from Notion:
- integration secret - notion_secret
- database id - notion_database_id

## TODO

- \[/] read Notion credentials from env variables
- \[/] format notion articles into markdown format
- \[o] Confluence integration
- \[o] format notion articles into html format for confluence // no markdown plugin for confluence
- \[o] Teams/RocketChat integration
- \[/] update Notion articles with "published date"
- \[ ] Mail integration? Like mail to d.ozog to communicate new issue to wider audience?
