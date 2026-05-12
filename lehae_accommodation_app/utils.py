import random

def generate_otp():
    return str(random.randint(100000, 999999))



def mask_email(email):
    try:
        name, domain = email.split("@")

        # mask name part
        if len(name) <= 2:
            masked_name = name[0] + "*"
        else:
            masked_name = name[0] + "*" * (len(name) - 2) + name[-1]

        # mask domain part (gmail.com → g***.com)
        domain_parts = domain.split(".")
        domain_name = domain_parts[0]
        extension = domain_parts[1] if len(domain_parts) > 1 else ""

        if len(domain_name) <= 2:
            masked_domain = domain_name[0] + "*"
        else:
            masked_domain = domain_name[0] + "*" * (len(domain_name) - 2) + domain_name[-1]

        return f"{masked_name}@{masked_domain}.{extension}"

    except:
        return email