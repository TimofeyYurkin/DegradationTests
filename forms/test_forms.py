from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, FieldList, FormField, SelectField, RadioField
from wtforms.validators import DataRequired, Length


# Мини-формы вопроса для создания тестов
class QuestionCreateForm(FlaskForm):
    title = StringField('Заголовок вопроса', validators=[DataRequired(), Length(min=10, max=60)])
    answer_1 = StringField('Ответ №1:', validators=[DataRequired(), Length(min=3, max=40)])
    answer_2 = StringField('Ответ №2:', validators=[DataRequired(), Length(min=3, max=40)])
    answer_3 = StringField('Ответ №3:', validators=[DataRequired(), Length(min=3, max=40)])
    answer_4 = StringField('Ответ №4:', validators=[DataRequired(), Length(min=3, max=40)])


class QuestionPercent(QuestionCreateForm):
    choose_per_1 = SelectField(choices=[('0', 0), ('7', 7), ('14', 14), ('20', 20)], validators=[DataRequired()])
    choose_per_2 = SelectField(choices=[('0', 0), ('7', 7), ('14', 14), ('20', 20)], validators=[DataRequired()])
    choose_per_3 = SelectField(choices=[('0', 0), ('7', 7), ('14', 14), ('20', 20)], validators=[DataRequired()])
    choose_per_4 = SelectField(choices=[('0', 0), ('7', 7), ('14', 14), ('20', 20)], validators=[DataRequired()])


class QuestionNumbers(QuestionCreateForm):
    choose_num_1 = SelectField(choices=[('1', 1), ('2', 2), ('3', 3), ('4', 4)], validators=[DataRequired()])
    choose_num_2 = SelectField(choices=[('1', 1), ('2', 2), ('3', 3), ('4', 4)], validators=[DataRequired()])
    choose_num_3 = SelectField(choices=[('1', 1), ('2', 2), ('3', 3), ('4', 4)], validators=[DataRequired()])
    choose_num_4 = SelectField(choices=[('1', 1), ('2', 2), ('3', 3), ('4', 4)], validators=[DataRequired()])


# Мини-форма вопроса для прохождения тестов
class QuestionAnswerForm(FlaskForm):
    answer_variants = RadioField('', choices=[('', ''), ('', ''), ('', ''), ('', '')], validators=[DataRequired()])


# Формы теста для их создания
class TestCreateForm(FlaskForm):
    test_title = StringField(validators=[DataRequired(), Length(min=3, max=30)])
    test_description = TextAreaField('Описание теста:', validators=[DataRequired(), Length(min=30, max=150)])
    privacy = BooleanField('Отображать для других пользователей')
    submit = SubmitField('Опубликовать')


class TestPercentForm(TestCreateForm):
    questions = FieldList(FormField(QuestionPercent), min_entries=5, max_entries=5)
    result_per_1 = StringField('Комментарий к 0% - 25%:', validators=[DataRequired(), Length(min=10, max=50)])
    result_per_2 = StringField('Комментарий к 26% - 50%:', validators=[DataRequired(), Length(min=10, max=50)])
    result_per_3 = StringField('Комментарий к 51% - 75%:', validators=[DataRequired(), Length(min=10, max=50)])
    result_per_4 = StringField('Комментарий к 76% - 100%:', validators=[DataRequired(), Length(min=10, max=50)])


class TestNumbersForm(TestCreateForm):
    questions = FieldList(FormField(QuestionNumbers), min_entries=5, max_entries=5)
    result_num_1 = StringField('Комментарий к варианту №1:', validators=[DataRequired(), Length(min=10, max=50)])
    result_num_2 = StringField('Комментарий к варианту №2:', validators=[DataRequired(), Length(min=10, max=50)])
    result_num_3 = StringField('Комментарий к варианту №3:', validators=[DataRequired(), Length(min=10, max=50)])
    result_num_4 = StringField('Комментарий к варианту №4:', validators=[DataRequired(), Length(min=10, max=50)])


# Форма теста для прохождения
class TestPassingForm(FlaskForm):
    variants = FieldList(FormField(QuestionAnswerForm), min_entries=5, max_entries=5)
    submit = SubmitField('Завершить')