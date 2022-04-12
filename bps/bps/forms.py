# from allauth.account.forms import SignupForm
# from django import forms

# class CustomSignupForm(SignupForm):
#     first_name = forms.CharField(max_length=30, label='First Name')
#     last_name = forms.CharField(max_length=30, label='Last Name')
#     phone = forms.CharField(max_length=10, min_length=10, label='phone')
#     gender = forms.CharField(max_length=30, label='gender')
#     dob = forms.DateField(label='dob')
#     address = forms.CharField(max_length=30, label='address')

#     def signup(self, request, user):
#         user.first_name = self.cleaned_data['first_name']
#         user.last_name = self.cleaned_data['last_name']
#         user.phone = self.cleaned_data['phone']
#         user.gender = self.cleaned_data['gender']
#         user.dob = self.cleaned_data['dob']
#         user.address = self.cleaned_data['address']
#         user.save()
#         return user
