from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, FieldList, FormField, SelectField
from wtforms.validators import DataRequired, Length


class QuestionCreateForm(FlaskForm):
    title = StringField('Заголовок вопроса', validators=[DataRequired(), Length(min=10, max=50)])
    answer_1 = StringField('Ответ №1:', validators=[DataRequired(), Length(min=5, max=30)])
    answer_2 = StringField('Ответ №2:', validators=[DataRequired(), Length(min=5, max=30)])
    answer_3 = StringField('Ответ №3:', validators=[DataRequired(), Length(min=5, max=30)])
    answer_4 = StringField('Ответ №4:', validators=[DataRequired(), Length(min=5, max=30)])


class QuestionAnswerForm(FlaskForm):
    pass


class QuestionPercent(QuestionCreateForm):
    choose_per_1 = SelectField(choices=[('1', 0), ('2', 5), ('3', 10)], validators=[DataRequired()])
    choose_per_2 = SelectField(choices=[('1', 0), ('2', 5), ('3', 10)], validators=[DataRequired()])
    choose_per_3 = SelectField(choices=[('1', 0), ('2', 5), ('3', 10)], validators=[DataRequired()])
    choose_per_4 = SelectField(choices=[('1', 0), ('2', 5), ('3', 10)], validators=[DataRequired()])


class QuestionNumbers(QuestionCreateForm):
    choose_num_1 = SelectField(choices=[('1', 1), ('2', 2), ('3', 3), ('4', 4)], validators=[DataRequired()])
    choose_num_2 = SelectField(choices=[('1', 1), ('2', 2), ('3', 3), ('4', 4)], validators=[DataRequired()])
    choose_num_3 = SelectField(choices=[('1', 1), ('2', 2), ('3', 3), ('4', 4)], validators=[DataRequired()])
    choose_num_4 = SelectField(choices=[('1', 1), ('2', 2), ('3', 3), ('4', 4)], validators=[DataRequired()])


class TestCreateForm(FlaskForm):
    test_title = StringField(validators=[DataRequired(), Length(min=3, max=30, message='31')])
    test_description = TextAreaField('Описание теста:', validators=[DataRequired(), Length(min=20, max=150)])
    privacy = BooleanField('Отображать для других пользователей')
    submit = SubmitField('Создать')


class TestPercentForm(TestCreateForm):
    questions = FieldList(FormField(QuestionPercent), min_entries=10, max_entries=10)
    result_per_1 = StringField('Комментарий к 0% - 25%:', validators=[DataRequired(), Length(min=10, max=50)])
    result_per_2 = StringField('Комментарий к 30% - 50%:', validators=[DataRequired(), Length(min=10, max=50)])
    result_per_3 = StringField('Комментарий к 55% - 75%:', validators=[DataRequired(), Length(min=10, max=50)])
    result_per_4 = StringField('Комментарий к 80% - 100%:', validators=[DataRequired(), Length(min=10, max=50)])


class TestNumbersForm(TestCreateForm):
    questions = FieldList(FormField(QuestionNumbers), min_entries=10, max_entries=10)
    result_num_1 = StringField('Комментарий к варианту №1:', validators=[DataRequired(), Length(min=10, max=50)])
    result_num_2 = StringField('Комментарий к варианту №2:', validators=[DataRequired(), Length(min=10, max=50)])
    result_num_3 = StringField('Комментарий к варианту №3:', validators=[DataRequired(), Length(min=10, max=50)])
    result_num_4 = StringField('Комментарий к варианту №4:', validators=[DataRequired(), Length(min=10, max=50)])


class PassingForm(FlaskForm):
    pass