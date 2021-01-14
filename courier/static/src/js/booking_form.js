odoo.define('courier.booking_form', function(require) {
    'use strict';
    var ajax = require('web.ajax');
    var Model = require('web.Model');


    $(document).ready(function() {
              getPagination('#table-id');
					//getPagination('.table-class');
					//getPagination('table');

		  /*					PAGINATION 
		  - on change max rows select options fade out all rows gt option value mx = 5
		  - append pagination list as per numbers of rows / max rows option (20row/5= 4pages )
		  - each pagination li on click -> fade out all tr gt max rows * li num and (5*pagenum 2 = 10 rows)
		  - fade out all tr lt max rows * li num - max rows ((5*pagenum 2 = 10) - 5)
		  - fade in all tr between (maxRows*PageNum) and (maxRows*pageNum)- MaxRows 
		  */


function getPagination(table) {
  var lastPage = 1;

  $('#maxRows')
    .on('change', function(evt) {
      //$('.paginationprev').html('');						// reset pagination

     lastPage = 1;
      $('.pagination')
        .find('li')
        .slice(1, -1)
        .remove();
      var trnum = 0; // reset tr counter
      var maxRows = parseInt($(this).val()); // get Max Rows from select option

      if (maxRows == 5000) {
        $('.pagination').hide();
      } else {
        $('.pagination').show();
      }

      var totalRows = $(table + ' tbody tr').length; // numbers of rows
      $(table + ' tr:gt(0)').each(function() {
        // each TR in  table and not the header
        trnum++; // Start Counter
        if (trnum > maxRows) {
          // if tr number gt maxRows

          $(this).hide(); // fade it out
        }
        if (trnum <= maxRows) {
          $(this).show();
        } // else fade in Important in case if it ..
      }); //  was fade out to fade it in
      if (totalRows > maxRows) {
        // if tr total rows gt max rows option
        var pagenum = Math.ceil(totalRows / maxRows); // ceil total(rows/maxrows) to get ..
        //	numbers of pages
        for (var i = 1; i <= pagenum; ) {
          // for each page append pagination li
          $('.pagination #prev')
            .before(
              '<li data-page="' +
                i +
                '">\
								  <span>' +
                i++ +
                '<span class="sr-only">(current)</span></span>\
								</li>'
            )
            .show();
        } // end for i
      } // end if row count > max rows
      $('.pagination [data-page="1"]').addClass('active'); // add active class to the first li
      $('.pagination li').on('click', function(evt) {
        // on click each page
        evt.stopImmediatePropagation();
        evt.preventDefault();
        var pageNum = $(this).attr('data-page'); // get it's number

        var maxRows = parseInt($('#maxRows').val()); // get Max Rows from select option

        if (pageNum == 'prev') {
          if (lastPage == 1) {
            return;
          }
          pageNum = --lastPage;
        }
        if (pageNum == 'next') {
          if (lastPage == $('.pagination li').length - 2) {
            return;
          }
          pageNum = ++lastPage;
        }

        lastPage = pageNum;
        var trIndex = 0; // reset tr counter
        $('.pagination li').removeClass('active'); // remove active class from all li
        $('.pagination [data-page="' + lastPage + '"]').addClass('active'); // add active class to the clicked
        // $(this).addClass('active');					// add active class to the clicked
	  	limitPagging();
        $(table + ' tr:gt(0)').each(function() {
          // each tr in table not the header
          trIndex++; // tr index counter
          // if tr index gt maxRows*pageNum or lt maxRows*pageNum-maxRows fade if out
          if (
            trIndex > maxRows * pageNum ||
            trIndex <= maxRows * pageNum - maxRows
          ) {
            $(this).hide();
          } else {
            $(this).show();
          } //else fade in
        }); // end of for each tr in table
      }); // end of on click pagination list
	  limitPagging();
    })
    .val(5)
    .change();

  // end of on select change

  // END OF PAGINATION
}

function limitPagging(){
	// alert($('.pagination li').length)

	if($('.pagination li').length > 7 ){
			if( $('.pagination li.active').attr('data-page') <= 3 ){
			$('.pagination li:gt(5)').hide();
			$('.pagination li:lt(5)').show();
			$('.pagination [data-page="next"]').show();
		}if ($('.pagination li.active').attr('data-page') > 3){
			$('.pagination li:gt(0)').hide();
			$('.pagination [data-page="next"]').show();
			for( let i = ( parseInt($('.pagination li.active').attr('data-page'))  -2 )  ; i <= ( parseInt($('.pagination li.active').attr('data-page'))  + 2 ) ; i++ ){
				$('.pagination [data-page="'+i+'"]').show();

			}

		}
	}
}

$(function() {
  // Just to append id number for each row
  $('table tr:eq(0)').prepend('<th> ID </th>');

  var id = 0;

  $('table tr:gt(0)').each(function() {
    id++;
    $(this).prepend('<td>' + id + '</td>');
  });
});

//  Developed By Yasser Mas
// yasser.mas2@gmail.com
    
    
    

        $("#bulk_import_form").on("click", ".download_import_file", function (e) {
                e.preventDefault();
                var model = new Model('courier.courier').call('download_file_format', []).then(function(result) {
                if (result) {
                    window.location = result;
                } else {
                    alert('No Data');
                }
            })
          });

        $('#courier_booking .confirm_booking').change(function(e) {
                e.preventDefault();
                var is_proceed = true;
                $('#courier_booking  input[required="1"]').each(function() {
                    var value = $(this).val();
                    if (value.length == 0) {
                        is_proceed = false;
                    }
                });
                if (is_proceed) {
                    $('#courier_booking').submit();
                }
                else{
                alert("kindly fill the form ");
                }

         });
        $('#courier_booking #delivery_location_ids').change(function(e) {
           var selected_board_id = $(this).val();
           var partner_id = $('#courier_booking #receiver_id').val();
           var post={}
           if(selected_value==0){
            if(partner_id==0 || partner_id==null){
                    $('#courier_booking .receiver_span').removeClass("hide");
                    $('#courier_booking #receiver_id').addClass("mandatory_field");

            }else{
                    return ajax.jsonRpc('/create/location', 'call', post).then(function(modal) {
                        if (modal === false) {
                            $button.prop('disabled', false);
                            return;
                        }
                        var $modal = $(modal);
                        $modal.modal();
                        $modal.on('click', '.close_dpopup', function(e) {
                            $modal.modal('hide');
                        });
                        $modal.on('click', '.submit_cpopup', function(e) {
                        var is_proceed = true;
                        $modal.find('#address_detail_view  input,select[required="1"]').each(function() {
                            var value = $(this).val();
                            if (value.length == 0) {
                                is_proceed = false;
                                $(this).addClass("mandatory_field");
                            }
                        });
                        if(is_proceed){
                              var datastring ={}
                              datastring['partner_id'] = partner_id;
                              datastring['street'] = $modal.find("#street").val();
                              datastring['street2'] = $modal.find("#street2").val();
                              datastring['city'] = $modal.find("#city").val();
                              datastring['state_id'] = $modal.find("#state_id").val();
                              datastring['country_id'] = $modal.find("#country_id").val();
                              return ajax.jsonRpc('/create/location', 'call', datastring).then(function(modal_view) {
                                    var f = modal_view;
                                    var option = document.createElement("option");
                                    option.text = datastring['name'];
                                    option.value = modal_view;
                                    var s = '<option selected=true id=' + modal_view +' value=' + modal_view + '>' + datastring['street'] + '</option>';
                                    $('#courier_booking').find("#delivery_location_ids").append(s);
                                    $modal.modal('hide');
                                });
                                }
                                else{

                                //$modal.find('#address_detail_view').submit();
                                }
                        });

                    });
            }
            }
      });

        $('#courier_booking .add_area').click(function(e) {
            var selected_value = $(this).val();
            var post=[];
            return ajax.jsonRpc('/create/add_area_view', 'call', post).then(function(modal) {
                if (modal === false) {
                    $button.prop('disabled', false);
                    return;
                }
                var $modal = $(modal);
                $modal.modal();
                $modal.on('click', '.close_dpopup', function(e) {
                    $modal.modal('hide');
                });
                $modal.on('click', '.submit_cpopup', function(e) {
                        var is_proceed = true;
                        $modal.find('#area_popup  input,select[required="1"]').each(function() {
                            var value = $(this).val();
                            if (value.length == 0) {
                                is_proceed = false;
                                $(this).addClass("mandatory_field");
                            }
                        });
                        if(is_proceed){
                                  var datastring ={}
                                  datastring['area'] = $modal.find("#area").val();
                                  datastring['zone_id'] = $modal.find("#zone_id").val();
                                  return ajax.jsonRpc('/create/add_area_view', 'call', datastring).then(function(modal_view) {
                                        var f = modal_view;
                                        var option = document.createElement("option");
                                        option.text = datastring['name'];
                                        option.value = modal_view;
                                        var s = '<option selected=true zone_id='+datastring['zone_id']+'+id=' + modal_view +' value=' + modal_view + '>' + datastring['area'] + '</option>';
                                        $('#courier_booking').find("#sender_area_id").append(s);
                                        $('#courier_booking').find("#recevier_area_id").append(s);
                                        $modal.modal('hide');
                              });
                        }

                    });
                });
        });
    $('#courier_booking .add_location').click(function(e) {
            var selected_value = $(this).val();
            var partner_id = $('#courier_booking #sender_id').val();
            var post={};
            if(selected_value==0){
            if(partner_id==0 || partner_id==null){

               $('#courier_booking .sender_span').removeClass("hide");
               $('#courier_booking #sender_id').addClass("mandatory_field");
            }
            else{
            return ajax.jsonRpc('/create/location', 'call', post).then(function(modal) {
                if (modal === false) {
                    $button.prop('disabled', false);
                    return;
                }
                var $modal = $(modal);
                $modal.modal();
                $modal.on('click', '.close_dpopup', function(e) {
                    $modal.modal('hide');
                });
                $modal.on('click', '.submit_cpopup', function(e) {
                var is_proceed = true;
                        $modal.find('#address_detail_view  input,select[required="1"]').each(function() {
                            var value = $(this).val();
                            if (value.length == 0) {
                                is_proceed = false;
                                $(this).addClass("mandatory_field");
                            }
                        });
                        if(is_proceed){
                      var datastring ={}
                      datastring['partner_id'] = partner_id;
                      datastring['street'] = $modal.find("#street").val();
                      datastring['street2'] = $modal.find("#street2").val();
                      datastring['city'] = $modal.find("#city").val();
                      datastring['state_id'] = $modal.find("#state_id").val();
                      datastring['country_id'] = $modal.find("#country_id").val();
                        datastring['area_id'] = $modal.find("#area_id").val();
                          datastring['zip'] = $modal.find("#zip").val();
                      return ajax.jsonRpc('/create/location', 'call', datastring).then(function(modal_view) {
                            var f = modal_view;
                            var option = document.createElement("option");
                            option.text = datastring['name'];
                            option.value = modal_view;
                            var s = '<option selected=true id=' + modal_view +' value=' + modal_view + '>' + datastring['street'] + '</option>';
                            $('#courier_booking').find("#pickup_location_id").append(s);
                            $modal.modal('hide');
                        });
                        }

                });
            });
            }
            }
        });
     $('#courier_booking #courier_method').change(function(e) {
            var selected_value = $(this).val();
            if(selected_value=="pickup_and_delivery"){
                $('#courier_booking .pickup_datediv').removeClass("hide");
                $('#courier_booking .pickup_locationdiv').removeClass("hide");
                $('#courier_booking #pickup_location_id').prop('required',true);
                $('#courier_booking #pickupdate').prop('required',true);
                $('#courier_booking #pickuptime').prop('required',true);
            }
            else{
                $('#courier_booking .pickup_datediv').addClass("hide");
                $('#courier_booking .pickup_locationdiv').addClass("hide");
                $('#courier_booking #pickup_location_id').prop('required',false);
                $('#courier_booking #pickupdate').prop('required',false);
                $('#courier_booking #pickuptime').prop('required',false);
            }

       });

     $('#courier_booking .booking_level').change(function(e) {
        var booking_level_value = $(this).val();
        var selected_grade_options = "";
        if (booking_level_value=='domestic_delivery')
            {
                $("#courier_booking .country").empty();
                $("#courier_booking .country").append("<option value='2'>United Arab Emirates</option>");
                $("#courier_booking .dynamic_area").addClass("hide");
                $("#courier_booking .areadiv").removeClass("added_neware_div");

            }
            else if(booking_level_value=='international_delivery'){
                $("#courier_booking .hidden_country option").each(function() {
                    var value = $(this).val();
                    var text =$(this).text();
                        selected_grade_options = selected_grade_options + ('<option  value=' + value + '>' + text + '</option>');

                });
                console.log(selected_grade_options)
                $("#courier_booking .country").append(selected_grade_options);
                $("#courier_booking .dynamic_area").removeClass("hide");
                $("#courier_booking .areadiv").addClass("added_neware_div");
            }

     });

     $('#courier_booking .add_partner').click(function(e) {
            var id =$(this).attr("record_id");
            var post=[];
            return ajax.jsonRpc('/create/partner', 'call', post).then(function(modal) {
                    if (modal === false) {
                        $button.prop('disabled', false);
                        return;
                    }
                    var $modal = $(modal);
                    $modal.modal();
                    $modal.on('click', '.close_dpopup', function(e) {
                        $modal.modal('hide');
                    });
                    $modal.on('click', '.submit_cpopup', function(e) {
                          var datastring ={}
                          datastring['name'] = $modal.find("#name").val();
                          datastring['phone'] = $modal.find("#phone").val();
                          datastring['street'] = $modal.find("#street").val();
                          datastring['street2'] = $modal.find("#street2").val();
                          datastring['city'] = $modal.find("#city").val();
                          datastring['state_id'] = $modal.find("#state_id").val();
                          datastring['area_id'] = $modal.find("#area_id").val();
                          datastring['zip'] = $modal.find("#zip").val();
                          datastring['country_id'] = $modal.find("#country_id").val();
                          return ajax.jsonRpc('/create/partner', 'call', datastring).then(function(modal_view) {
                                var f = modal_view;
                                var option = document.createElement("option");
                                option.text = datastring['name'];
                                option.value = modal_view;
                                var s = '<option selected=true id=' + modal_view +' zip='+datastring['zip']+' city='+datastring['city']+' state_id='+datastring['state_id']+' area_id='+datastring['area_id']+' country_id='+datastring['country_id']+' street='+datastring['street']+' street2='+datastring['street2']+' value=' + modal_view + '>' + datastring['name'] + '</option>';

                                $('#courier_booking').find("#"+id).append(s);
                                $modal.modal('hide');
                            });
                    });
                });


     });

     $('#courier_booking .partner').change(function(e) {
            var selected_value = $(this).val();
            var id =$(this).attr("id");
             var selected_school_id = $(this).val();
                var street=$(this).children('option:selected').attr("street");
                var street2=$(this).children('option:selected').attr("street2");
                var city=$(this).children('option:selected').attr("city");
                var state_id=$(this).children('option:selected').attr("state_id");
                var zip =$(this).children('option:selected').attr("zip");
                var country_id=$(this).children('option:selected').attr("country_id");
                var area_id =$(this).children('option:selected').attr("area_id");
            if(selected_value==0){
            var post=[];
            return ajax.jsonRpc('/create/partner', 'call', post).then(function(modal) {
                    if (modal === false) {
                        $button.prop('disabled', false);
                        return;
                    }
                    var $modal = $(modal);
                    $modal.modal();
                    $modal.on('click', '.close_dpopup', function(e) {
                        $modal.modal('hide');
                    });
                    $modal.on('click', '.submit_cpopup', function(e) {
                          var datastring ={}
                          datastring['name'] = $modal.find("#name").val();
                          datastring['phone'] = $modal.find("#phone").val();
                          datastring['street'] = $modal.find("#street1").val();
                          datastring['street2'] = $modal.find("#street2").val();
                          datastring['city'] = $modal.find("#city").val();
                          datastring['state_id'] = $modal.find("#state_id").val();
                          datastring['country_id'] = $modal.find("#country_id").val();
                          return ajax.jsonRpc('/create/partner', 'call', datastring).then(function(modal_view) {
                                var f = modal_view;
                                var option = document.createElement("option");
                                option.text = datastring['name'];
                                option.value = modal_view;
                                var s = '<option selected=true id=' + modal_view +' value=' + modal_view + '>' + datastring['name'] + '</option>';
                                $('#courier_booking').find("#"+id).append(s);
                                $('#courier_booking').find("#"+id).append(s);
                                $modal.modal('hide');
                            });
                    });
                });
            }
            else{
                var selected_partner_id = selected_value;
                var selected_grade_options = "";
                // filter on grade field.
                $("#courier_booking #hide_location_list option").each(function() {
                    var partner_id = $(this).attr("partner_id");
                    var location_id = $(this).val();
                    var address =$(this).text();
                    if (selected_partner_id == partner_id) {
                        selected_grade_options = selected_grade_options + ('<option partner_id=' + selected_partner_id + ' value=' + location_id + '>' + address + '</option>');
                    }
                });
                if(id=="sender_id")
                {   $("#courier_booking #pickup_location_id").empty();
                    $("#courier_booking #pickup_location_id").append("<option disabled='1' value=''>Location..</option>");
                    $("#courier_booking #pickup_location_id").append("<option value='0'>Create Location..</option>");

                    $("#courier_booking #pickup_location_id").append(selected_grade_options);

                    $("#courier_booking #sender_street").val(street);
                    $("#courier_booking #sender_street2").val(street2);
                    $("#courier_booking #sender_city").val(city);
                    $("#courier_booking #sender_zip").val(zip);
                    if (state_id!="res.country.state()"){
                        var sender_state_id = String(state_id).replace("res.country.state(","")
                        var ss_state_id = String(sender_state_id).replace(",)","");
                        $("#courier_booking #sender_state_id").val(ss_state_id);
                        }
                    if (area_id!="area.area()"){
                        var sender_ss_area_id = String(area_id).replace("area.area(","")
                        var ss_area_id = String(sender_ss_area_id).replace(",)","");
                        console.log("s"+ss_area_id)
                        $("#courier_booking #sender_area_id").val(ss_area_id);
                        }
                    if (country_id!="res.country()"){
                        var sender_country_id = String(country_id).replace("res.country(","")
                        var ss_country_id = String(sender_country_id).replace(",)","");
                        console.log("ss_country_id"+ss_country_id);
                        $("#courier_booking #sender_country_id").val(ss_country_id);
                        }
                }
                if(id=="receiver_id"){
                    $("#courier_booking #delivery_location_ids").empty();
                    $("#courier_booking #delivery_location_ids").append("<option disabled='1' value=''>Location..</option>");
                    $("#courier_booking #delivery_location_ids").append("<option value='0'>Create Location..</option>");
                    $("#courier_booking #delivery_location_ids").append(selected_grade_options);
                    $("#courier_booking #receiver_street").val(street);
                    $("#courier_booking #receiver_street2").val(street2);
                    $("#courier_booking #receiver_city").val(city);
                    $("#courier_booking #receiver_zip").val(zip);
                    if (state_id!="res.country.state()"){
                        var receiver_state_id = String(state_id).replace("res.country.state(","")
                        var rr_state_id = String(receiver_state_id).replace(",)","");
                        $("#courier_booking #receiver_state_id").val(rr_state_id);
                        }
                    if (area_id!="area.area()"){
                        var receiver_ss_area_id = String(area_id).replace("area.area(","")
                        var rr_area_id = String(receiver_ss_area_id).replace(",)","");
                        $("#courier_booking #receiver_area_id").val(rr_area_id);
                        }
                    if (country_id!="res.country()"){
                        var receiver_country_id = String(country_id).replace("res.country(","")
                        var rr_country_id = String(receiver_country_id).replace(",)","");
                        $("#courier_booking #receiver_country_id").val(rr_country_id);
                        }
               }

           }

        });
     });
    });