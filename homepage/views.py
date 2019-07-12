from django.shortcuts import render

def index(request):
    """View function for home page of site."""
    #get the information about the weekday, the date and if it is a holiday
    from datetime import date
    date = date.today()
    month = date.month
    day = date.day
    weekday = date.weekday()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    months = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    holidays = ['7-9', '12-10', '2-11', '15-11', '24-12', '25-12', '31-12']
    date_test = str(day) + '-' + str(month)
    if date_test in holidays:
        holiday = True
    elif weekday > 4:
        holiday = True
    else:
        holiday = False
    context = {
        'weekday': days[weekday],
        'day': day,
        'month': months[month],
        'holiday': holiday
    }
    return render(request, 'index.html', context=context)

def about(request):
    return render(request, 'about.html')
