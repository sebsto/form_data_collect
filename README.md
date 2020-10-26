This is a generic web services to accept HTML form content

## Build 

sam build 

## Deploy 

The first time, use `sam deploy --guided`.

For subsequent deployments, use:

`sam build && sam deploy --config-env dev`

## Local invoke Lambda function 

```bash
AWS_PROFILE=seb
sam build && sam local invoke --profil $AWS_PROFILE -e events/event.json -n events/environment.json
```

## Call API Gateway

```bash
AWS_REGION=eu-central-1
AWS_HTTP_API=vija6eqvi4
curl -v -H "Origin: http://localhost:1313"  -H "Content-type: application/x-www-form-urlencoded" -X POST --data name=seb&email=seb@stormacq.com https://$AWS_HTTP_API.execute-api.$AWS_REGION.amazonaws.com/prod/form      
````

## Logs 

```bash
sam logs --profile $AWS_PROFILE --region $AWS_REGION --name FormDataCollectFunction --stack-name form-data-collect
```

## Integration from HTML

### HTML

```html 
<!-- https://mdbootstrap.com/md-bootstrap-cdn/ -->

<!-- Font Awesome -->
<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.8.2/css/all.css">
<!-- Google Fonts -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap">
<!-- Bootstrap core CSS -->
<link href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.5.0/css/bootstrap.min.css" rel="stylesheet">
<!-- Material Design Bootstrap -->
<link href="https://cdnjs.cloudflare.com/ajax/libs/mdbootstrap/4.19.1/css/mdb.min.css" rel="stylesheet">
<!-- JQuery -->
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
<!-- Bootstrap tooltips -->
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.4/umd/popper.min.js"></script>
<!-- Bootstrap core JavaScript -->
<script type="text/javascript"
  src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.5.0/js/bootstrap.min.js"></script>
<!-- MDB core JavaScript -->
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mdbootstrap/4.19.1/js/mdb.min.js"></script>

<div class="modal fade" id="modalSubscriptionForm" tabindex="-1" role="dialog" aria-labelledby="myModalLabel"
  aria-hidden="true">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <form id="landing_email_form">
        <input type=hidden name="pk" value='nata.coach.landing_page'/>
        <input type=hidden name="sk" value='email'/>
        <div class="modal-header text-center">
          <h4 class="modal-title w-100 font-weight-bold">Subscribe</h4>
          <button type="button" class="close" data-dismiss="modal" aria-label="Close" id="modalSubscriptionFormClose">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body mx-3">
          <div class="md-form mb-5">
            <i class="fas fa-user prefix grey-text"></i>
            <input type="text" id="form3" name="name" class="form-control validate">
            <label data-error="wrong" data-success="right" for="form3">Your name</label>
          </div>

          <div class="md-form mb-4">
            <i class="fas fa-envelope prefix grey-text"></i>
            <input type="email" id="form2" name="email" class="form-control validate">
            <label data-error="wrong" data-success="right" for="form2">Your email</label>
          </div>

        </div>
        <div class="modal-footer d-flex justify-content-center">
          <button id ="landing_email_submit" class="btn btn-indigo">Send <i class="fas fa-paper-plane ml-1"></i></button>
        </div>
      </form>
    </div>
  </div>
</div>
````

```javascript
$(document).ready(function () {
    let POST_URL='https://vija6eqvi4.execute-api.eu-central-1.amazonaws.com/prod/form';
    let form = $('#landing_email_form'); // contact form
    let submit = $('#landing_email_submit'); // submit button

    // form submit event
    form.on('submit', function (e) {
        console.log("submit");
        e.preventDefault(); // prevent default form submit

        $.ajax({
            url: POST_URL, // form action url
            type: 'POST', // form submit method get/post
            dataType: 'html', // request type html/json/xml
            data: form.serialize(), // serialize form data
            beforeSend: function () {
                console.log("beforeSend");
                submit.html('Sending....'); // change submit button text
            },
            success: function (data) {
                console.log("success");
                form.trigger('reset'); // reset form
                submit.html('Send <i class="fas fa-paper-plane ml-1"></i>'); // change submit button text (not so nice to have HTNM markup here :-( )

                // hide the modal and restore the page background
                $('#modalSubscriptionForm').modal("hide");
                $('.modal-backdrop').remove()  
            },
            error: function (e) {
                console.log("error");
                console.log(e)
                form.trigger('reset'); // reset form
                submit.html('Error, try again later'); // change submit button text
            }
        });
    });
});
```