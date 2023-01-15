# PyNewsPublisher
#
# Notion api reference
#  https://developers.notion.com/reference/
#
from notion.client import NotionDbClient

notion_database_id = "<database_id>" # load from env or arg
notion_secret = "<secret>" #load from env or arg

if __name__ == "__main__":

    notionClient = NotionDbClient(notion_secret, notion_database_id)
    articlesList = notionClient.get_unpublished_articles()
    print ('Got ' + str(len(articlesList)) + ' articles')
    for article in articlesList:

        print(str(article))