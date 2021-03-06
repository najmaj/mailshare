/* License: https://github.com/RobFisher/mailshare/blob/master/LICENSE */

function get_email_body_element(email_id) {
    element_selector = "#body_" + email_id;
    return $(element_selector)
}

function scroll_to_position(position) {
    /* http://twigstechtips.blogspot.com/2010/02/jquery-animated-scroll-to-element.html */
    $('html,body').animate({ scrollTop: position },
        { duration: 'slow', easing: 'swing'});
}

function scroll_to_row(element) {
    body_row = element.parent();
    hidden_height = body_row.offset().top + body_row.height() -
        ($(window).scrollTop() + $(window).height());
    if(hidden_height > 0) {
        header_row = body_row.prev();
        if((body_row.height() + header_row.height()) < $(window).height()) {
            scroll_to_position($(window).scrollTop() + hidden_height);
        }
        else {
            scroll_to_position(header_row.offset().top);
        }
    }
}

function toggle_email_body(email_id) {
    element = get_email_body_element(email_id);
    if(element.hasClass("empty")) {
        element.toggleClass("empty showing");
        fetch_mail_body(email_id, $(element));
    }
    else if(element.hasClass("shown")) {
        element.toggleClass("shown hidden");
    }
    else if(element.hasClass("hidden")) {
        element.toggleClass("hidden shown");
        scroll_to_row(element);
    }
}

function fetch_mail_body(email_id) {
    Dajaxice.mailshare.mailshareapp.fetch_mail_body(Dajax.process,{'email_id':email_id,'url':location.href})
}

function update_mail_body(data) {
    element = get_email_body_element(data.email_id);
    element.html(data.email_body);
    element.toggleClass("showing shown");
    scroll_to_row(element);
}

tag_response_callback = null;
function fetch_tag_completion(request, response) {
    tag_response_callback = response;
    Dajaxice.mailshare.mailshareapp.fetch_tag_completion(Dajax.process,{'text':request.term});
}

function update_tag_completion(data) {
    if(tag_response_callback) {
        tag_response_callback(data.tags);
    }
}

function add_tag(email_id) {
    $("#tagbutton_" + email_id).toggleClass("shown hidden");
    tagbox=$("#tagbox_" + email_id);
    tagbox.toggleClass("hidden shown");
    tagbox.autocomplete({source: fetch_tag_completion,
                         select: tag_select_callback(email_id)});
    tagbox.focus();
}

function fetch_add_tag(email_id, text) {
    if(email_id == -1) {
	Dajaxice.mailshare.mailshareapp.fetch_multi_add_tag(Dajax.process,{'selected_mails':selected_mails,'tag':text, 'url':location.href});
    }
    else {
	Dajaxice.mailshare.mailshareapp.fetch_add_tag(Dajax.process,{'email_id':email_id,'tag':text, 'url':location.href});
    }
}

function fetch_delete_tag(email_id, tag_id) {
    if(email_id == -1) {
	var answer = confirm("Deleting a tag from selected emails cannot be undone.");
        if(answer) {
	    Dajaxice.mailshare.mailshareapp.fetch_multi_delete_tag(Dajax.process,{'selected_mails':selected_mails,'tag_id':tag_id, 'url':location.href});
        }
    }
    else {
        Dajaxice.mailshare.mailshareapp.fetch_delete_tag(Dajax.process,{'email_id':email_id,'tag_id':tag_id, 'url':location.href});
    }
    return false;
}

function tag_key(event, email_id) {
    if(event.keyCode == 13) {
        tagbox=$("#tagbox_" + email_id);
        fetch_add_tag(email_id, tagbox.val());
    }
}

/* for explanation see http://stackoverflow.com/questions/939032/jquery-pass-more-parameters-into-callback */
var tag_select_callback=function tag_selected(email_id) {
    return function(event, ui) {
        fetch_add_tag(email_id, ui.item.value);
    }
}

function update_tags(data) {
    $("#taglist_" + data.email_id).html(data.tags_html);
    $("#tagbox_" + data.email_id).val('');
    if(data.propagate) {
        fetch_multibar(false);
    }
}

function tagbox_blur(email_id) {
    $("#tagbox_" + email_id).toggleClass("shown hidden");
    $("#tagbutton_" + email_id).toggleClass("shown hidden");
}

function fetch_delete_mail(email_id) {
    var answer = confirm("This will permanently delete the email from the Mailshare database.");
    if(answer) {
	Dajaxice.mailshare.mailshareapp.fetch_delete_mail(Dajax.process,{'email_id':email_id});
    }
}

function update_delete_mail(success) {
    if(success) {
	window.location.reload();
    }
    else {
	alert("Unable to delete email.");
    }
}

var selected_mails = [];
function select_email(mail_id) {
    selected_mails.push(mail_id);
}

function unselect_email(mail_id) {
    selected_mails.splice($.inArray(mail_id, selected_mails), 1);
}

function fetch_multibar(propagate) {
    Dajaxice.mailshare.mailshareapp.fetch_multibar(Dajax.process,{'selected_mails':selected_mails, 'propagate':propagate, 'url':location.href});
}

function update_multibar(data) {
    var identifier;
    if(data.tags_only) {
        identifier = "#multi_bar_tag_list";
    }
    else {
        identifier = "#multi_bar_tags";
    }
    if(data.tags_html != '') {
        $(identifier).html(data.tags_html);
    }
    else {
        $(identifier).html("Select emails to view and edit their tags.");
    }
    $("#tagbox_-1").val('');
    if(data.tags_changed && data.propagate) {
	fetch_open_mail_tags();
    }
}

function fetch_open_mail_tags() {
    $('span[id^="taglist_"]').each(function(i) {
        var email_id = parseInt(this.id.substr(8));
	Dajaxice.mailshare.mailshareapp.fetch_mail_tags(Dajax.process,{'email_id':email_id, 'url':location.href});
    });
}

function update_tag_cloud(data) {
    $(".tag_cloud").html(data.tag_cloud_html);
}

function checkbox_clicked(checkbox, mail_id) {
    if(checkbox.checked) {
	select_email(mail_id);
    }
    else {
	unselect_email(mail_id);
    }
    fetch_multibar(true);
}

function invert_selection() {
    $(".mailcheck").each(function(i) {
	var mail_id = parseInt(this.name.substr(6));
	if(this.checked) {
	    unselect_email(mail_id);
	    this.checked = false;
	}
	else {
	    select_email(mail_id);
	    this.checked = true;
	}
    });
    fetch_multibar(true);
}

function select_all_or_none() {
    var select_all = true;
    if(selected_mails.length > 0) {
        select_all = false;
    }
    $(".mailcheck").each(function(i) {
	var mail_id = parseInt(this.name.substr(6));
        if(this.checked && !select_all) {
            unselect_email(mail_id);
            this.checked = false;
        }
        else if(!this.checked && select_all) {
            select_email(mail_id);
            this.checked = true;
        }
    });
    fetch_multibar(true);
}

function document_ready_function() {
    $(".mailcheck").each(function(i) {
	var mail_id = parseInt(this.name.substr(6));
        if(this.checked) {
            select_email(mail_id);
	}
    });
    if(selected_mails.length > 0) {
        fetch_multibar(true);
    }
}

$(document).ready(document_ready_function);
