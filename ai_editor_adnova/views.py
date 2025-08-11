# -*- coding: utf-8 -*-
import os
from django.shortcuts import render, redirect
# import google.generativeai as genai # УДАЛЯЕМ эту строку
from django.conf import settings
from django.http import HttpResponse
from .forms import Step1Form, Step2Form, Step3Form
from django.urls import reverse
import json
import markdown
import google.generativeai as genai

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

GEMINI_MODEL = 'gemini-1.5-flash'

try:
    # Инициализируем клиент OpenAI, оборачиваем в try/except на случай ошибок с ключом
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось инициализировать клиент OpenAI. Правильно ли установлен OPENAI_API_KEY? Ошибка: {e}")
    # Вы можете установить client в None, чтобы обработать это позже
    client = None

required_keys = ['company_name', 'product_description', 'competitors',
                     'problem_solve', 'price_category', 'customer']
Steps_config ={
    '1':{'form': Step1Form,'template': 'step1.html','next_url_name':'step2'},
    '2':{'form': Step2Form,'template': 'step2.html','next_url_name':'step3'},
    '3':{'form': Step3Form,'template': 'step3.html','next_url_name':'results'},
}

def multi_step_form_view(request, step_number):
    current_step_config = Steps_config.get(str(step_number))
    if not current_step_config:
        return redirect('step1')
    formclass = current_step_config['form']
    template_name = current_step_config['template']
    next_url_name = current_step_config['next_url_name']

    if 'form_data' not in request.session:
        request.session['form_data'] = {}

    if request.method == 'POST':
        form = formclass(request.POST)
        if form.is_valid():
            request.session['form_data'].update(form.cleaned_data)
            request.session.modified = True
            print(f"DEBUG (Step {step_number}): Session data after update: {request.session.get('form_data')}")
            print(f"DEBUG (Step {step_number}): Required keys for check: {required_keys}")
            if str(step_number) == '3':
                return redirect('loading')
            else:
                return redirect(next_url_name)
        else:
            print(f"DEBUG (Step {step_number}): Form is NOT valid. Errors: {form.errors}")
    else:
        initial_data = request.session['form_data']
        form = formclass(initial={k: v for k, v in initial_data.items() if k in formclass.base_fields})
    context = {
        'form': form,
        'current_step': step_number,
        'total_steps': len(Steps_config)
    }
    return render(request, template_name, context)

def results_view(request):
    """Обрабатывает последний шаг, вызывает OpenAI API и отображает результат."""
    generated_html = None

    all_collected_data = request.session.get('form_data', {})

    print("\n--- ОТЛАДКА: Данные, собранные в сессии для results_view ---")
    print(f"Собранные данные: {all_collected_data}")
    print(f"Обязательные ключи: {required_keys}")
    print(f"Результат проверки (все ключи присутствуют?): {all(key in all_collected_data for key in required_keys)}")
    print("---------------------------------------------------\n")
    # ------------------------------------

    
    generated_text = "Please complete all steps of the form to obtain the result." # Дефолтный текст
    

    # Проверяем, что все необходимые данные собраны перед запросом к OpenAI
    if all(key in all_collected_data for key in required_keys):
        try:
            # Формируем промпт для OpenAI, используя все собранные данные
            # OpenAI использует формат "messages" для чат-комплиций
            prompt_template = (
                f"""You are an experienced marketing strategist with a deep understanding of market segmentation, psychological triggers, and customer journey mapping. Your task is to generate a highly detailed and actionable profile of a single, typical target audience persona for the specified product/service using the provided information. Focus on both demographic and psychographic aspects, and analyze how the product directly addresses the persona’s core pain points.

Product/Service for Analysis:
Product/Service Name:{all_collected_data['company_name']}
Product/Service Description:{all_collected_data['product_description']}
Key Differentiator/USP:{all_collected_data['competitors']}
Primary Problem Solved:{all_collected_data['problem_solve']}
Price Category/Average Price:{all_collected_data['price_category']}
Target Audience (Initial User Idea):{all_collected_data['customer']}

Task:
Use all provided information to generate a comprehensive persona profile for the product/service described above (no further questions needed).Do exactly as written in the prompt.
All information must be formatted as Markdown lists. Use only the headings and classes provided below. **Do not add any introductions, conclusions, extra sections, paragraphs, or blank lines. Just return the generated text in the specified structure.
<div class="container"
<span class="title_persona">Persona Profile Structure</span>
    <div class="container_person">
        <div class="container_in_container"
        <div class="con_in_con_con">
            <div class="persona-name">
            Assign a realistic first name and second name to this persona.In one line 
            </div>
            <div class="left-aligned-content">
            <div class="container_demograghics">
                Leave 4 spaces between the text and the answer.
                Age  <span class="field-age">Specify a precise age (e.g., 35).</span> 
                Field of Work/Industry  <span class="field-industry">Indicate their occupation or industry. (If B2B context, specify their role or position.)</span> 
                Location  <span class="field-location">Specify the type of location (e.g., city, suburb, rural, specific region).</span>  
                Family Status  <span class="field-family-status">Describe marital status and family (e.g., married with children).</span> 
            </div>
            </div>
        </div>



<div class="psychotype" > 
    <div class="psychographics">
        <h1 class="title_psychographics">Hobbies & Interests</h1>
        <h2 class="field-hobbies">Provide 3–5 specific examples of their hobbies or interests that hint at their needs or priorities.</h2>
    </div>

    <div class="channels">
        <h1 class="title_channels" >Preferred Advertising Channels</h1>
        <h2 class="field-channels">From the user-provided channels, indicate which platforms best reach this persona.</h2>
    </div>

    <div class="challenges" >
        <h1 class="title_challenges"Daily Challenges/Frustrations</h1>
        <h2 class="field-frustrations">Describe their typical day and recurring issues related to the problem the product solves.</h2>
    </div>
</div>

<div class="pain" >
    <h1 class="title_pain">Core Pain Points (Directly Solvable by Product)</h1>
    <div class="pain-points">
        <p class="emothional_deep" >Identify 2–3 deep emotional or practical pains related to the primary problem.</p>
        <p class="explain_pain">Explain how these pains manifest in their life with <strong>concrete examples</strong> (not vague).</p>
    </div>
</div>


<div class="budget"
    <h1 class="title_budget">Budget & Willingness to Pay</h1>
    <div class="explain">
        <p class="willing_pay" >Explain why this persona is willing to pay for a solution given their income and the product’s price range.</p>  
        <p class="what_justifies" >What justifies the cost for them?</p>
    </div>
</div>

<div class="media_habits"
    <div class="media"
        <h1 class="title_media" >Information Consumption & Media</h1>
        <div class="info-habits">
            <h1 class="where" >Where do he/she seek solutions or information?
            <h2 class="field-info-sources">(e.g., industry blogs, specific social media platforms, online forums, YouTube tutorials, podcasts, professional communities)</h2>
        </div>
    </div>

    <div class="content_type">
        <h1 class="what" >What type of content does he/she prefer?</h1>  
        <h2 class="field-content-type">(e.g., long-form articles, short videos, webinars, quick tips)</h2>
    </div>

    <div class="trust" >
        <h1 class="who">Who does he/she trust for recommendations?</h1>
        <h2 class="field-trusted-sources">(e.g., industry experts, peer reviews, influencers)</h2>
    </div>
</div>

<div class="solves" >
    <h1 class="title_solves" >How the Product Solves her/his Pains</h1
    <div class="solution">
    Provide a <strong>narrative</strong> explaining how the product’s Key Differentiator/USP directly addresses each core pain point.  
    Use the persona’s daily context.  
    <strong>Example:</strong>  
    > “For [Persona Name], who dreads [Pain Point], [Product/Service Name]’s [Feature/USP] completely automates [Specific Task], freeing up their evenings for [Desired Outcome].”
    </div>
</div>

<div class="potential" >
    <h1 class="title_potential" >Potential Objections/Hesitations</h1>
    <h2 class="objections">
    List common doubts or resistance this persona might have before committing to the product/service.
    </h2>
</div>


##  Response Format Requirements:
-Do exactly as written in the prompt!!!
- Present the persona in a clear, narrative, and engaging style.   
- Ensure every point is specific and provides actionable insights, not vague generalities.  
- Maintain a professional, empathetic, and data-driven tone.
-Do not use "" and <p>```html</p>!
-Use <br> to move text to a new line, when there are more than 8 words in line 1
</div>
</div>
"""
            )




            
            prompt_content = prompt_template.encode('utf-8').decode('utf-8')
            # Вызов Gemini API
            model = genai.GenerativeModel(GEMINI_MODEL)
            response = model.generate_content(prompt_content)
            generated_text = response.text

            generated_html = markdown.markdown(generated_text, 
            extensions=['markdown.extensions.attr_list']
        )

        except Exception as e:
            print(f"\n--- Gemini API Error (DEBUG) ---")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {e}")
            print(f"-----------------------------------\n")
            generated_text = f"An error occurred while generating ideas with Gemini: {e}. Please ensure your API key is correctly set and try again."
    else:
        return redirect('step1')

    if 'form_data' in request.session:
        del request.session['form_data']
        request.session.modified = True

    context = {
        'generated_content': generated_html,
        'all_collected_data': all_collected_data
    }
    return render(request, 'results.html', context, content_type='text/html; charset=utf-8')


def loading(request):
    return render(request,'loading.html')

def about(request):
    return render(request, 'index.html')