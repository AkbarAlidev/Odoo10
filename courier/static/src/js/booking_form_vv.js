odoo.define('courier.booking_form', function(require) {
    'use strict';
    var ajax = require('web.ajax');
     $(document).ready(function() {




     $('#courier_booking .create_partner').change(function(e) {
            var selected_board_id = $(this).val();
            alert("d"+selected_board_id);
            var post=[];
            post['name'] ="janaki";
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
                $modal.on('click', '.email_cpopup', function(e) {
                        var datastring ={}
                      datastring['name'] = $modal.find("#name").val();
                      datastring['phone'] = $modal.find("#phone").val();
                      datastring['street1'] = $modal.find("#street1").val();
                      datastring['street2'] = $modal.find("#street2").val();
                      datastring['city'] = $modal.find("#city").val();
                      datastring['state_id'] = $modal.find("#state_id").val();
                      datastring['country_id'] = $modal.find("#country_id").val();
                      return ajax.jsonRpc('/create/partner', 'call', datastring).then(function(modal_view) {
                            var f = modal_view;
                            alert("f"+modal_view);
                            var option = document.createElement("option");
                            option.text = datastring['name'];
                            option.value = modal_view;
                            var s = '<option selected=true id=' + modal_view +' value=' + modal_view + '>' + datastring['name'] + '</option>';
                            $('#courier_booking').find("#sender_id").append(s);
//                            $('#courier_booking').find("#sender_id").value=modal_view;
                            $modal.modal('hide');
                        });
//                    alert("datastring"+datastring);
//                    $modal.modal('hide');
                });
            });

        });
     });
    });