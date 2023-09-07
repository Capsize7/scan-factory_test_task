import sqlite3
from collections import namedtuple


def get_regexp_for_garbage_domain(database, domain_table, regexp_table):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    sqlite_select_query = f'SELECT * from {domain_table}'
    cursor.execute(sqlite_select_query)
    row = cursor.fetchone()
    count_per_domain = {}
    count_of_projects = set()
    domains = namedtuple('Row', ['domain', 'project_id', 'change_part'])

    while row:
        project_id, name = row
        count_of_projects.add(project_id)
        first_split = name.find('.')
        left_part = name[:first_split]
        right_part = name[first_split + 1:]
        template_of_domain = domains(right_part, project_id, len(left_part))
        count_per_domain[template_of_domain] = count_per_domain.setdefault(template_of_domain, 0) + 1
        row = cursor.fetchone()

    for project in sorted(count_per_domain, key=lambda x: (count_per_domain[x]), reverse=True) \
            [:len(count_of_projects)]:
        regular_template = '(.)*' + '\.' + '(' + project.domain.replace(".", "\.") + ')' + '$'
        sqlite_select_query = f'INSERT INTO {regexp_table}(project_id, regexp) VALUES(?, ?)'
        cursor.execute(sqlite_select_query, (project.project_id, regular_template))
    connection.commit()
    connection.close()


if __name__ == '__main__':
    get_regexp_for_garbage_domain(database='domains.db', domain_table='domains', regexp_table='rules')
