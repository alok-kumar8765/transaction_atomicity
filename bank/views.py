from django.http import response
from django.http.response import Http404
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect, HttpResponse
import http
from .forms import Payment
from .models import customer
from django.db.models import F
import decimal
from django.db import transaction
from django.contrib import messages

'''
Atomicity = Atomicity is the defining property of database transactions. 
            atomic allows us to create a block of code within which the atomicity on the database is guaranteed. 
            If the block of code is successfully completed, the changes are committed to the database. 
            If there is an exception, the changes are rolled back.
Transaction = A transaction is an atomic set of database queries. These functions take a using argument 
              which should be the name of a database. If it isn’t provided, Django uses the “default” database.
              or in simple words 
              It is a sequence of one or more SQL operations that are treated as a unit.which means all operations
              should be executed successfully in order to call the transaction successful.
'''

### Part 1
# def process_payment(request):
#   try:
#     if request.method == 'POST':
#       form = Payment(request.POST)
#       if form.is_valid():
#         x = form.cleaned_data['payor']
#         y = form.cleaned_data['payee']
#         z = decimal.Decimal(form.cleaned_data['amount'])

#         payor = customer.objects.get(name=x)
#         payor.balance -= z
#         payor.save()

#         payee = customer.objects.get(name=y)
#         payee.balance += z
#         payee.save()

#         messages.info(request, 'Transaction Successfully Completed.')
#         return HttpResponseRedirect('/')
    
#     else:
#       form = Payment()
#       message= 'something went wrong'
#     return render(request, 'index.html', {'form': form,'message':message})

#   except Exception as e:
#     messages.info(request, 'User Does Not Exist')
#     return HttpResponseRedirect('/')

### Part 2 :
'''
We can use Atomicity in 2 ways, the first one is using decorator and second one is using as a context manager.

'''
@transaction.atomic
def process_payment(request):
  sid = transaction.savepoint()   # doc refrence point 1
  try:
    if request.method == 'POST':
      form = Payment(request.POST)
      if form.is_valid():
        x = form.cleaned_data['payor']
        y = form.cleaned_data['payee']
        z = decimal.Decimal(form.cleaned_data['amount'])

        payor = customer.objects.select_for_update().get(name=x)    # doc refrence point 2
        payee = customer.objects.select_for_update().get(name=y)

      # with transaction.atomic():
        payor.balance -= z
        payor.save()
        sid = transaction.savepoint()
        payee.balance += z
        payee.save()

        if payee:
          transaction.savepoint_commit(sid)                       # doc refrence point 4
          messages.info(request, 'Your Transaction has been Done successfully!')
          # return redirect('/')
          return render(request, 'index.html',{'form': form})
          
    else:
      form = Payment()
      # messages.info(request, 'Welcome to Transaction Page')
      return render(request, 'index.html', {'form': form})

  except Exception as e:
    transaction.savepoint_rollback(sid)                         # doc refrence point 4
    messages.info(request, 'Your Transaction has been rollback!')
    return redirect('/')


###### part 2
# def process_payment(request):
#   try:
#     if request.method == 'POST':

#       form = Payment(request.POST)

#       if form.is_valid():
#         x = form.cleaned_data['payor']
#         y = form.cleaned_data['payee']
#         z = decimal.Decimal(form.cleaned_data['amount'])

#         payor = customer.objects.select_for_update().get(name=x)
#         payee = customer.objects.select_for_update().get(name=y)

#       with transaction.atomic():
#         payor.balance -= z
#         payor.save()

#         payee.balance += z
#         payee.save()

#       messages.info(request, 'Your Transaction has been Done successfully!')

#       return redirect('/')
#     else:
#       form = Payment()
#       # messages.info(request, 'something went wrong')
#     return render(request, 'index.html', {'form': form})
    
#   except Exception as e:
#     messages.info(request, 'Donot Exist')
#     return render(request, 'index.html',{'form': form})