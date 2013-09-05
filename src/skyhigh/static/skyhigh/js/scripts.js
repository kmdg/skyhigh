$(document).ready(function(){

    /* Search */
    $("#header .search").click(function() {
        $(this).find('form').show();
    });

    /* Slider */
    $('#promo').anythingSlider({
        buildStartStop  : false,
        //autoPlay        : true,
        delay           : 5000,
        startPanel      : 1,
        hashTags        : false
    });

	/* Dropdown */
	$('#nav li').hover(
         function () {
           $(this).addClass('over');
           $(this).find('ul:first').show();
         }, 
         function () {
           $(this).removeClass('over');
           $(this).find('ul').hide();
         }
     );

    /* Partnership Approval */
    $('#partnership_approve_link').live('click', function(){
       var self = this;

        $.get($(self).attr('href'), function(data) {
            var table = $(self).parent().parent().parent(),
                num_rows = (table.children('tr').length);

            $(self).parent().parent().remove();

            if(num_rows == 1)
            {
                table.append('<tr><td colspan="5">Sorry, there are no partnership approvals pending</td></tr>');
            }
        });

        return false;
    });

    /* Evaluation Approval */
    $('#evaluation_approve_link').live('click', function(){
        var self = this;

        $.get($(self).attr('href'), function(data) {
            var table = $(self).parent().parent().parent(),
                num_rows = (table.children('tr').length);

            $(self).parent().parent().remove();

            if(num_rows == 1)
            {
                table.append('<tr><td colspan="5">Sorry, there are no evaluation approvals pending</td></tr>');
            }
        });

        return false;
    });

    /* Datepicker */
    $('#id_start_date').datePicker();
    $('#id_end_date').datePicker();

    /* Tags */
    $(".tag_open").live("click", function() {
        $(".tag_popup").hide();
        $(this).parent().find(".tag_popup").show();
    });
    $(".close").live("click", function() {
        $(this).parent().parent().hide();
    });
    $(".tag_action").live("click", function() {
        var form = $(this).parent();
        var tag_block = form.closest("div[class^='tags']");
        form.children("#id_action").val($(this).attr("id"));

        $.post(form.attr("action"), form.serialize(), function(data){
            tag_block.replaceWith(data);
        });
    });

    $('input[name="tag"]').live("keydown", function(event){
        if(event.which == 13){
            event.preventDefault();
            var form = $(this).parent();
            var tag_block = form.closest("div[class^='tags']");
            form.children("#id_action").val("save");

            $.post(form.attr("action"), form.serialize(), function(data){
                tag_block.replaceWith(data);
            });
        }
    });

    //Tag Popup
    $(".bulk_tag_open").click(function() {
        $(this).parent().find(".bulk_tag_popup").show();
    });
    $(".bulk_tag_action").click(function() {
        $("form#frmBulkTag #id_selected").val(get_bulk_ids());
        $("form#frmBulkTag #id_action").val($(this).attr("id"));
        $("form#frmBulkTag").submit();
        $(this).parent().parent().hide();
    });

    //Form Validation
    var PWD_MIN_CHAR = 8,
        PWD_MAX_CHAR = 45;

    $.validator.addMethod("password", function( value, element ) {
        var result = this.optional(element) || new RegExp("(?=^.{"+PWD_MIN_CHAR+","+PWD_MAX_CHAR+"}$)((?=.*\\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[^A-Za-z0-9]))^.*").test(value);
        return result;
    }, "Valid password should contain at least "+PWD_MIN_CHAR+" alphanumeric characters. Contain both upper and lower case letters. Contain at least one number (for example, 0-9). Contain at least one special character (for example,!@#$%^&*()+=-[]\\\';,./{}|\":?~_>)");

    $('#frmRegister').validate();
    $('#frmNewsLetter').validate();
    $('#frmCompleteSignup').validate();
    $('#frmEvaluationRequest').validate();
    $('#frmCSPPartner').validate();
    $('#frmTechnologyPartner').validate();
    $('#frmChannelPartner').validate();
    //$('#frmLogin').validate();
    $('.field > .errorlist').parent().addClass('has_error');

    /* Create/Edit Partner Console */
    $('#id_partner_type').change(function(event){
        var value = $(this).val();

        if(value == 0){
            $('#technology_row').show();
            $('#channel_row').hide();
        }
        else{
            $('#technology_row').hide();
            $('#channel_row').show();
        }
    });
    $('#id_partner_type').change();

    /* Technology partner application CSP */
    $('#id_technology_partner_subtype').click(function(event){
        var value = $(this).attr('checked');

        if(value == 'checked'){
            $('#csp_row').show();
        }
        else{
            $('#csp_row').hide();
        }
    });

    if(!$('#id_technology_partner_subtype').attr('checked')){
        $('#csp_row').hide();
    }
    
    /* Product eval */
    $('#id_upload_log_file_sample').click(function(event){
        var value = $(this).attr('checked');

        if(value == 'checked'){
            $('#static_page_row').show();
        }
        else{
            $('#static_page_row').hide();
        }
    });

    if(!$('#id_upload_log_file_sample').attr('checked')){
        $('#static_page_row').hide();
    }

    //General chops, mostly for stupid IE
    $('table td p:first-child').css({"margin-top":"0"});
    $('table td p:last-child').css({"margin-bottom":"0"});
    $('#nav ul ul li:last-child').css({"border":"0"});
    $('#footer .menu .sitemap ul:last-child').css({"padding-right":"0"});
    $('.section div .item:last-child').css({"border":"0"});
    $('.section ul.partners li:last-child').css({"padding":"0"});
    $('.content .column h3:first-child').css({"margin-top":"0"});
    $('.content .sidebar h3:first-child').css({"margin-top":"0"});
    $('.listing:last-child').css({"margin-bottom":"0", "border-bottom":""});
    $('.half:nth-child(2n)').css({"margin-right":"0"});
    $('.third:nth-child(3n)').css({"margin-right":"0"});
    $('.widget:last-child').css({"margin-bottom":"0", "border-bottom":""});
    $('.console .filter .row .field:last-child').css({"margin":"0"});
    $('.complete_profile .field:nth-child(2n)').addClass('align-right');

    //Toggle Filter
    $('.toggle-filter').click(function(){
        $(this).parent().find('.filter').toggle();
    });

    /* Outbound email colorbox */
    $('.outbound_email_lightbox').colorbox();

    /* Media Coverage etc. photos */
    $('#id_image').click(function() {
        $('#image_choice_new').attr('checked', true);
    });

    $('#id_existing_image').click(function() {
        $('#image_choice_existing').attr('checked', true);
    });

    $('#id_existing_image').change(function() {

        $.get('/console/news/and/events/content/image/url/' + $('#id_existing_image').attr('data-content-type') + '/' + $("#id_existing_image option:selected").val(), function(data) {
            data = JSON.parse(data);
            $('#image_choice_existing_preview').attr('src', data.url);
        });
    });

    $('.open_pop').colorbox();
    
    /* Chosen */
    $(".chzn_select").chosen();

    /* Mobile */
    $('.mobile_handle').click(function(){
        $(this).toggleClass('on');
        $('#header .search, #header .actions, #nav').toggle();
    });

    /* Mobile Conditional */
    if (($('#wrap').width()) < 960)
    {

        //Prepend the clock image
        $('.demo').prepend('<img src="/static/skyhigh/img/icon_demo.png" />');

        //Rip out the sidebar, and append it below
        $('.sidebar').appendTo('.content');

    }

    /* Console Tab flip */
    $(".tab_content").hide();
    $(".tabs li:first").addClass("on").show();
    $(".tab_content:first").show();
    $(".tabs a").click(function() {
        $(".tabs li").removeClass("on");
        $(this).parent().addClass("on");
        $(".tab_content").hide(); //Hide all tab content
        var activeTab = $(this).attr("rel"); //Find the rel attribute value to identify the active tab + content
        $(activeTab).fadeIn(); //Fade in the active content
        return false;
    });

    /* Leadership content flip */
    $('.listing .listing_image_left .desc p:first-child').show();
    $('.leader_desc_show').click(function(){
        var $this = $(this);
        $(this).parent().parent().find('.desc p').toggle();
        $this.text($this.text() == "Show Less" ? "Show More" : "Show Less");
        $('.listing .listing_image_left .desc p:first-child').show();
    });

    /* 30 30 Terms toggle */
    $('.thirty_terms h4 a').click(function(){
        $('.thirty_terms > div').toggle();
    });


});