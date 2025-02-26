import re
from flask import Flask, render_template, request
from search import Search

app = Flask(__name__)

es = Search()


@app.get('/')
def index():
    return render_template('index.html')


# This is where the searching operation is made
@app.post('/')
def handle_search():
    query = request.form.get('query', '')
    filters, parsed_query = extract_filters(query)
    from_ = request.form.get('from_', type=int, default=0)


    if parsed_query:
        search_query = {
            'must': {
                'multi_match': {
                    'query': parsed_query,
                    'fields': ['name', 'summary', 'content'],
                }
            }
        }
    else:
        search_query = {
            'must': {
                'match_all': {}
            }
        }


    results = es.search(
        query={
            'bool': {
                **search_query,
                **filters
            }
        },

        aggs={

            'category-agg': {
                'terms': {
                    'field': 'where_to_buy.keyword',
                    'size' : 5
                }
            },

            'total_price-agg': {
                'terms': {
                    'field': 'price_usd',
                    'size': 10
                },
            },
        },


        size=5,
        from_=from_
    )


    aggs = {
        'Where to buy': {
            bucket['key']: bucket['doc_count']
            for bucket in results['aggregations']['category-agg']['buckets']
            if bucket['doc_count'] > 0
        },
        'Price': {
            bucket['key']: bucket['doc_count']
            for bucket in results['aggregations']['total_price-agg']['buckets']
            if bucket['doc_count'] > 0
        },
    }
    return render_template('index.html', results=results['hits']['hits'],
                           query=query, from_=from_,
                           total=results['hits']['total']['value'], aggs=aggs)

 

                           
#query is the text entered by the user in the form
#response['hits']['hits'] the list of search results.
#response['hits']['total'] the total number of results that are available
# When we use query multi_match we have the possibility to serach in more than one variable
# Size determine the number of result display on a page 
# 

@app.get('/document/<id>')
def get_document(id):
    document = es.retrieve_document(id)
    title = document['_source']['name']
    paragraphs = document['_source']['description'].split('\n')
    return render_template('document.html', title=title, paragraphs=paragraphs)


# To make the reindex method easier to invoke , call and used
# This decorator is used to mark a function as a custom CLI command.
@app.cli.command()
def reindex():
    """Regenerate the Elasticsearch index."""
    response = es.reindex()
    print(f'Index with {len(response["items"])} documents created '
          f'in {response["took"]} milliseconds.')



#Function responsible for filtering results
def extract_filters(query):
    filters = []

    filter_regex = r'category:([^\s]+)\s*'
    m = re.search(filter_regex, query)
    if m:
        filters.append({
            'term': {
                'category.keyword': {
                    'value': m.group(1)
                }
            },
        })
        query = re.sub(filter_regex, '', query).strip()

    filter_regex = r'year:([^\s]+)\s*'
    m = re.search(filter_regex, query)
    if m:
        filters.append({
            'range': {
                'updated_at': {
                    'gte': f'{m.group(1)}||/y',
                    'lte': f'{m.group(1)}||/y',
                }
            },
        })
        query = re.sub(filter_regex, '', query).strip()

    return {'filter': filters}, query







"""
@app.post('/')
def handle_search():
    query = request.form.get('query', '')
    filters, parsed_query = extract_filters(query)
    from_ = request.form.get('from_', type=int, default=0)


    if parsed_query:
        search_query = {
            'must': {
                'multi_match': {
                    'query': parsed_query,
                    'fields': ['name', 'description', 'how_to_use'],
                }
            }
        }
    else:
        search_query = {
            'must': {
                'match_all': {}
            }
        }


    results = es.search(
        query={
            'bool': {
                **search_query,
                **filters
            }
        },
        aggs={
            'category-agg': {
                'terms': {
                    'field': 'category.keyword',
                }
            },
            'year-agg': {
                'date_histogram': {
                    'field': 'updated_at',
                    'calendar_interval': 'year',
                    'format': 'yyyy',
                },
            },
        },
        size=5,
        from_=from_
    )


    aggs = {
        'Category': {
            bucket['key']: bucket['doc_count']
            for bucket in results['aggregations']['category-agg']['buckets']
        },
        'Year': {
            bucket['key_as_string']: bucket['doc_count']
            for bucket in results['aggregations']['year-agg']['buckets']
            if bucket['doc_count'] > 0
        },
    }
    return render_template('index.html', results=results['hits']['hits'],
                           query=query, from_=from_,
                           total=results['hits']['total']['value'], aggs=aggs)
"""
