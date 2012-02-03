/* License: https://github.com/RobFisher/mailshare/blob/master/LICENSE */

function fetch_index_tag_cloud() {
    team_box = $("#team");
    team_id = team_box.val();
    Dajaxice.mailshare.mailshareapp.fetch_index_tag_cloud(Dajax.process,{'team_id':team_id});
}

function document_ready_function() {
    fetch_index_tag_cloud();
}

function update_index_tag_cloud(data) {
    $(".tag_cloud").html(data.tag_cloud_html);
}

$(document).ready(document_ready_function);
