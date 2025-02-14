from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from django.shortcuts import redirect
from django.urls import reverse
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime

def index(request):
    return HttpResponse("Rango says hey there partner! <br><a href='/rango/about/'>About Page</a>")

def about(request):
    visitor_cookie_handler(request)  # Ensure cookies are updated before retrieving visits
    visits = request.session.get('visits', 1)  # Retrieve visits count

    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()

    return HttpResponse(f"Rango says here is the about page. <br>Visits: {visits} <br><a href='/rango/'>Back to Index</a>")

    
def index(request):

    category_list = Category.objects.exclude(name='Test').order_by('-likes')[:5]
    
    most_viewed_pages = Page.objects.exclude(title='Test').order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['most_viewed_pages'] = most_viewed_pages

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session.get('visits', 1)
    
    response = render(request, 'rango/index.html', context=context_dict)
    return response


def show_category(request, category_name_slug):
    context_dict = {}

    try:
        # Fetch the category using the slug provided.
        category = Category.objects.get(slug=category_name_slug)

        # Fetch the pages related to the category excluding "Test" and limit the pages to the top 5 based on views.
        pages = Page.objects.filter(category=category).exclude(title='Test').order_by('-views')[:5]

        # Add category and pages to context.
        context_dict['category'] = category
        context_dict['pages'] = pages

    except Category.DoesNotExist:
        # If the category does not exist, set both to None.
        context_dict['category'] = None
        context_dict['pages'] = None

    # Render the template with context.
    return render(request, 'rango/category.html', context_dict)



@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            # Save the new category to the database.
            new_category = form.save(commit=True)
            # Redirect to the newly created category's page using reverse.
            return redirect(reverse('rango:show_category', kwargs={'category_name_slug': new_category.slug}))
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    # Redirect if category doesn't exist
    if category is None:
        return redirect('/rango/')

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0  # Set initial views
                page.save()
                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)


def register(request):
    # A boolean value for telling the template whether the registration was successful.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves,
            # we set commit=False. This delays saving the model
            # until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and
            # put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to indicate that the template
            # registration was successful.
            registered = True
        else:
            # Invalid form or forms - mistakes or something else?
            # Print problems to the terminal.
            print(user_form.errors, profile_form.errors)
    else:
        # Not a HTTP POST, so we render our form using two ModelForm instances.
        # These forms will be blank, ready for user input.
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render(request, 'rango/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered
    })


def user_login(request):
    # If the request is a HTTP POST, try to extract login details
    if request.method == 'POST':
        # Get the username and password from the login form
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user:
            # Check if the account is active
            if user.is_active:
                # Log the user in and redirect to homepage
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # If account is disabled
                return HttpResponse("Your Rango account is disabled.")
        else:
            # If authentication fails, print details and return an error message
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    
    # If not a POST request, render the login form
    return render(request, 'rango/login.html')

def some_view(request):
    if not request.user.is_authenticated():
        return HttpResponse("You are logged in.")
    else:
        return HttpResponse("You are not logged in.")

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect(reverse('rango:index'))

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

# Updated the function definition
from datetime import datetime

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))  # Ensure integer conversion
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))

    if last_visit_cookie:
        last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    else:
        last_visit_time = datetime.now()

    # If it's been more than a day since the last visit, increment the count
    if (datetime.now() - last_visit_time).days > 0:
        visits += 1
        request.session['last_visit'] = str(datetime.now())  # Update last visit time
    else:
        request.session['last_visit'] = last_visit_cookie  # Preserve last visit time

    request.session['visits'] = visits  # Update visit count
    request.session.modified = True  # Ensure Django saves session data





# Create your views here.
