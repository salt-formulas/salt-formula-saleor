
==============
Saleor Formula
==============

Saleor is an opensource storefront platform for perfectionists.


Sample Metadata
===============

Simple site

.. code-block:: yaml

    saleor:
      server:
        store:
          demo:
            enabled: true
            secret_key: ${_param:saleor_secret_key}
            debug: False
            internal_ips: '127.0.0.1'
            bind:
              port: 8000
            # custom saleor source
            saleor:
              engine: git
              address: https://github.com/dresl/saleor
              revision: master
            database:
              engine: postgresql
              host: 127.0.0.1
              name: saleor_demo
              password: ${_param:saleor_demo_postgresql_password}
              user: saleor_demo
            time_zone: 'Europe/Prague'
            lang_code: 'en'
            languages:
            - cs
            - en
            country: CZ
            currency: CZK
            sendgrid:
              username: ${_param:saleor_sendgrid_username}
              password: ${_param:saleor_sendgrid_password}
            email:
              url: ${_param:saleor_email_url}
              backend: django.core.mail.backends.smtp.EmailBackend
              host_url: smtp.seznam.cz
              host:
                user: mail@example.com
                password: hostpassword
              port: 465
              use_tls: False
              use_ssl: True
            enable_ssl: False
            from_email:
              default: default-from@exmaple.com
              order: order-from@example.com
            account_activation_days: 3
            logout_on_password_change: False
            low_stock_threshold: 10
            max_cart_line_quantity: 50
            paginate_by: 16
            dashboard_paginate_by: 30
            dashboard_search_limit: 5
            allowed_hosts: '*, localhost'
            db_search_enabled: True
            # deployment-dependant elastic enviroment variable
            elasticsearch:
              url: ${_param:saleor_search_elasticsearch}
            searchbox:
              url: ${_param:saleor_search_searchbox}
            bonsai:
              url: ${_param:saleor_search_bonsai}
            extra_apps:
            - watermarker
            silk:
              enabled: False
            redis:
              url: ${_param:saleor_redis_url}
            openexchangerates:
              api_key: ${_param:saleor_openexchangerates_api_key}
            google:
              analytics_tracking_id: ${_param:saleor_google_analytics_tracking_id}
            vatlayer:
              api_endpoint: http://apilayer.net/api/
              access_key: 6ad86845f43a0307c15405347e9df9f8
            paypal:
              api_endpoint: https://api.sandbox.paypal.com
              client_id: ${_param:saleor_paypal_client_id}
              secret: ${_param:saleor_paypal_secret}
              capture: False
            payment_choices:
            - engine: paypal
              display_name: PayPal
            recaptcha:
              public_key: ${_param:saleor_recaptcha_public_key}
              private_key: ${_param:saleor_recaptcha_private_key}
            celery:
              broker_url: ${_param:saleor_celery_broker_url}
              cloudamqp_url: ${_param:saleor_celery_cloudamqp_url}
            sentry:
              dsn: ${_param:saleor_sentry_dsn}
            aws:
              access_key_id: ${_param:saleor_aws_access_key_id}
              location: ${_param:saleor_aws_location}
              media_bucket_name: ${_param:saleor_aws_media_bucket_name}
              media_custom_domain: ${_param:saleor_aws_media_custom_domain}
              querystring_auth: False
              static_custom_domain: ${_param:saleor_aws_static_custom_domain}
              secret_access_key: ${_param:saleor_aws_secret_access_key}
              storage_bucket_name: ${_param:saleor_aws_storage_bucket_name}


Read more
=========

* https://getsaleor.com/


Single saleor service

.. code-block:: yaml

    saleor:
      server:
        enabled: true


References
==========

* https://saleor.readthedocs.io/en/latest/index.html
* https://getsaleor.com/
* https://github.com/mirumee/saleor


Documentation and Bugs
======================

To learn how to install and update salt-formulas, consult the documentation
available online at:

    http://salt-formulas.readthedocs.io/

In the unfortunate event that bugs are discovered, they should be reported to
the appropriate issue tracker. Use GitHub issue tracker for specific salt
formula:

    https://github.com/salt-formulas/salt-formula-saleor/issues

For feature requests, bug reports or blueprints affecting entire ecosystem,
use Launchpad salt-formulas project:

    https://launchpad.net/salt-formulas

Developers wishing to work on the salt-formulas projects should always base
their work on master branch and submit pull request against specific formula.

You should also subscribe to mailing list (salt-formulas@freelists.org):

    https://www.freelists.org/list/salt-formulas

Any questions or feedback is always welcome so feel free to join our IRC
channel:

    #salt-formulas @ irc.freenode.net
