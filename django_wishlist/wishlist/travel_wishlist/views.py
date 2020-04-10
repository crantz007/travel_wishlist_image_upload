from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Place
from .forms import NewPlaceForm, TripReviewForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


# Create your views here.
@login_required
def place_list(request):
    """ If this is a POST request, the user clicked the Add button
       in the form. Check if the new place is valid, if so, save a
       new Place to the database, and redirect to this same page.
       This creates a GET request to this same route.
       If not a POST route, or Place is not valid, display a page with
       a list of places and a form to add a new place.
       """
    if request.method == 'POST':
        form = NewPlaceForm(request.POST)
        place = form.save(commit=False)  # Create a new Place from the form but don't save yet
        place.user = request.user  # associate the palce with the logged-in user
        if form.is_valid():  # Check against DB constraints , for example, are required fields present?
            place.save()  # save to database
            return redirect('place_list')  # redirects to GET view with name place_list - which is this same view

    # If not a POST , or the form is not valid , render the page
    # with the form to add q new place , and list of places
    places = Place.objects.filter(user=request.user).filter(visited=False).order_by('name')
    new_place_form = NewPlaceForm()
    return render(request, 'travel_wishlist/wishlist.html', {'places': places, 'new_place_form': new_place_form })


@login_required
def places_visited(request):
    visited = Place.objects.filter(user=request.user).filter(visited=True)
    return render(request, 'travel_wishlist/visited.html', {'visited': visited})


@login_required
def place_was_visited(request, place_pk):
    if request.method == 'POST':

        place = get_object_or_404(Place, pk=place_pk)
        print(place.user, request.user)
        if place.user == request.user:  # only let a user visit their own places
            place.visited = True
            place.save()

        else:
            return HttpResponseForbidden()

    return redirect('place_list')


@login_required
def place_details(request, place_pk):
    place = get_object_or_404(Place, pk=place_pk)

    if place.user != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = TripReviewForm(request.POST, request.FILES, instance=place)
        # instance is the model object to update with the form data

        if form.is_valid():
            form.save()
            messages.info(request, 'Trip information update!')

        else:
            messages.error(request, form.errors) # Temp error message - future version should improve
        return redirect('place_details', place_pk=place_pk)
    else: # GET place details
        if place.visited:
            review_form = TripReviewForm(instance=place) # Pre-populate with data from this Place instance
            return render(request, 'travel_wishlist/place_detail.html', {'place': place, 'review_form': review_form})
        else:
            return render(request, 'travel_wishlist/place_detail.html', {'place': place})


@login_required
def delete_place(request, place_pk):
    place = get_object_or_404(Place, pk=place_pk)
    if place.user == request.user:
        place.delete()
        return redirect('place_list')
    else:
        return HttpResponseForbidden()
