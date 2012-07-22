$(document).ready(function(){
    $('.plus').click(do_stuff);
    $(".more.multi").change(do_stuff_2);
});

function do_stuff(){
    that = $(this);
    that.before('<a class="btn btn-danger minus" href="#" onclick="$(this).prev().remove().end().remove(); return false;"><i class="icon-minus icon-white"></i></a>').before(that.prev().prev().clone())
    .prev().prev().val(that.val()).next().val("").focus();
}
function do_stuff_2(){
    that = $(this);
    that.before(that.clone()).before('<a class="btn btn-danger minus" href="#" onclick="$(this).prev().remove().end().remove(); return false;"><i class="icon-minus icon-white"></i></a>');
    that.val("").focus();
}
$.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (this.name === 'csrfmiddlewaretoken' || this.value === ''){}
        else if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

$(function() {
    $('form').submit(function() {
        // console.log(JSON.stringify($('form').serializeObject()));
        if ($("#keyword").val() === ""){
            // missing - but required
            $(".required").addClass("error");
            return false;
        }
        $.post('/post-submit-json/', {'csrfmiddlewaretoken':$('input[name="csrfmiddlewaretoken"]').val(),'keyword':$("#initial_search_term").val(), 'json':String(JSON.stringify($('#submit_json').serializeObject()))} );
        alert('ok');
        return false;
    });
});