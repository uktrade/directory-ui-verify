from django.template import Context, Template


def test_add_export_elements_classes():
    template = Template(
        '{% load add_export_elements_classes from export_elements_tags %}'
        '{{ html|add_export_elements_classes|safe }}'

    )
    context = Context({
        'html': (
            '<br/>'
            '<h1>Title zero</h1>'
            '<h2>Title one</h2>'
            '<h3>Title two</h3>'
            '<ul>List one</ul>'
            '<ol>List two</ol>'
        )
    })
    html = template.render(context)

    assert html == (
        '<br/>'
        '<h1 class="heading-xlarge">Title zero</h1>'
        '<h2 class="heading-large">Title one</h2>'
        '<h3 class="heading-medium">Title two</h3>'
        '<ul class="list list-bullet">List one</ul>'
        '<ol class="list list-number">List two</ol>'
    )
