from wtforms import RadioField
from wtforms.validators import DataRequired
from dmutils.forms import DmForm, StripWhitespaceStringField
from wtforms import TextAreaField
from work_order_data import questions


class WorkOrderSellerForm(DmForm):
    seller = RadioField(
        coerce=int,
        validators=[
            DataRequired(message='You must select a seller.')
        ]
    )

    def __init__(self, brief_id, data_api_client, *args, **kwargs):
        super(WorkOrderSellerForm, self).__init__(*args, **kwargs)

        responses = data_api_client.find_brief_responses(brief_id)
        self.seller.choices = [(br['supplierCode'], br['supplierName']) for br in responses['briefResponses']]


def FormFactory(slug, formdata=None):
    class WorkOrderQuestionForm(DmForm):
        heading = questions[slug]['heading']
        summary = questions[slug]['summary']

    type = questions[slug].get('type', None)
    if type == 'text':
        setattr(WorkOrderQuestionForm, slug, StripWhitespaceStringField(
            questions[slug]['label'],
            validators=[DataRequired(message=questions[slug]['message'])]
        ))
    elif type == 'address':
        setattr(WorkOrderQuestionForm, 'abn', StripWhitespaceStringField(
            questions[slug]['abn'],
            validators=[DataRequired(message=questions[slug]['abnMessage'])]))

        setattr(WorkOrderQuestionForm, 'name', StripWhitespaceStringField(
            questions[slug]['name'],
            validators=[DataRequired(message=questions[slug]['nameMessage'])]))

        setattr(WorkOrderQuestionForm, 'contact', StripWhitespaceStringField(
            questions[slug]['contact'],
            validators=[DataRequired(message=questions[slug]['contactMessage'])]))

    else:
        setattr(WorkOrderQuestionForm, slug, TextAreaField(
            questions[slug]['label'],
            validators=[DataRequired(message=questions[slug]['message'])]
        ))

    return WorkOrderQuestionForm(formdata=formdata)
