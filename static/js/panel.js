// Globals
PROFIT_INDEX = 6;
EBAYTAX_INDEX = 2;
PROMOTED_INDEX = 5;
ORIGIN_PARSEFLOAT = parseFloat;
parseFloat = function(value){
    return Math.round((ORIGIN_PARSEFLOAT(value) + Number.EPSILON) * 100) / 100;
}

/**
 * Adds a sum row at the end of the sales table.
 */
function sum_sales_table() {

    var result = [];
    
    // iterate over each row and find all the numbers that are needed to sum up.
    $('#table_sales > tbody > tr').each(function(){
        if ($(this).attr("id") != "bootstrap-overrides"){
            $('td.sumtable', this).each(function(index, val){
                // sum up the numbers and give in to result array.
                if(!result[index]) result[index] = 0;
                result[index] += parseFloat($(val).text());
            });
        }
    });
    
    // create and design the sum row
    $('#table_sales > tbody:last-child').append('<tr id="bootstrap-overrides" class="greenrow"></tr>');
    $('#table_sales > tbody:last-child > tr:last').append('<th class="align-middle"><i class="fa fa-hashtag fa-md"></i></th>');
    $('#table_sales > tbody:last-child > tr:last').append('<th>Total</th>');

    // print the sum row numbers
    $(result).each(function(i){
        if (i == PROFIT_INDEX){
            $('#table_sales > tbody:last-child > tr:last').append('<th id="total_sum_profit">'+ parseFloat(this) +'</th>')
        }
        else if (i == PROMOTED_INDEX){
            $('#table_sales > tbody:last-child > tr:last').append('<th id="total_sum_promoted">'+ parseFloat(this) +'</th>')
        }
        else if (i == EBAYTAX_INDEX){
            $('#table_sales > tbody:last-child > tr:last').append('<th id="total_sum_eBay_tax">'+ parseFloat(this) +'</th>')
        }
        else{
            $('#table_sales > tbody:last-child > tr:last').append('<th>'+ parseFloat(this) +'</th>')
        }
        
    });

    // fill out blank columns
    $('#table_sales > tbody:last-child > tr:last').append('<th></th>')
    $('#table_sales > tbody:last-child > tr:last').append('<th></th>')
}


/**
 * Calculates the profit from the add sale form inputs and prints it in the profit input.
 */
function calc_profit_form() {    
    // get the values
    ebay_price = $('#f_ebay_price').val();
    amazon_price = $('#f_amazon_price').val();
    ebay_tax = $('#f_ebay_tax').val();
    paypal_tax = $('#f_paypal_tax').val();
    tm_fee = $('#f_tm_fee').val();
    promoted = $('#f_promoted').val();
    discount = $("#f_discount").val();

    // print the profit
    $("#f_profit").val(ebay_price - amazon_price - ebay_tax - paypal_tax - tm_fee - promoted + discount);
}


/**
 * Subtracts the fees from the gift money, and prints it.
 */
function calc_add_to_balance() {
    
    // get the values
    gift_money = $('#f_gift_money').val();
    gift_tax = $('#f_gift_tax').val();

    // print the amount to add to balance
    $('#txt_balance_add').val(gift_money - gift_tax);
}


/**
 * Calculating the profit of all the sales shown on the screen minus the costs.
 */
function calc_total_date_profit(){
    // get the values
    profit = $("#total_sum_profit").text();

    costs = 0;
    $("#total-profit span.hidden-cost").each(function(){
        costs += parseFloat($(this).text());
    });

    gifts_tax = 0;
    selected_date = $("#s_sales_filter_by_date").val()

    $.ajax({
        url: "/filter_gifts",
        type: "GET",
        data: {
            date: selected_date,
        },
        success:function(data){
            $.each(data, function(i, item) {
                gifts_tax += parseFloat(item.fields.gift_tax);
            });
            // calculate the total profit
            if (isNaN(parseFloat(profit))){
                total = -1 * (parseFloat(costs) + parseFloat(gifts_tax))
            }
            else {
                total = parseFloat(profit) - parseFloat(costs) - parseFloat(gifts_tax)
            }

            // if the total profit is grater than 0, show it in green, else show it in red.
            if (total < 0) $("#total-profit").addClass("bg-danger") 
            else $("#total-profit").addClass("bg-success")
            
            $("#total-profit").html("$" + parseFloat(total))
        }
    })
    .fail(function(data){
        console.log(data);
        
    });

    
}


/** 
 * Sets the gifts date select to current month.
 */
function set_gifts_date(){

    // get the date values
    var today = new Date();
    year = today.getFullYear();
    month = today.getMonth() + 1;

    // iterate over all the dates. If the user has an option that matches the current month, select it.
    $("#s_filter_gifts_by_date option").each(function(){
        if ($(this).val() == year + '-' + month){
            $("#s_filter_gifts_by_date").val($(this).val());
            return false;
        }
    })

    // show the new data
    $('#s_filter_gifts_by_date').trigger("change");
}


/**
 * Sends a request to the server with the selected date range.
 * The backend processes the request and returnes all the relevant gifts in the time period.
 */
function filter_gifts_by_date(){
    $.ajax({
        url: "/filter_gifts",
        type: "GET",
        data: {
            date: $("#s_filter_gifts_by_date").val()
        },
        success:function(data){
            // clear table contents
            $("#table_gifts").html("<tbody id='gifts_table_body'></tbody>");
            
            // if there are gifts in this time period, create the table with the values from the server.
            if (!data.data){
                // create the table structure
                var headers = "<thead><tr class='headerrow-gift'><th scope='col'>Date</th><th scope='col'>Gift Amount</th><th scope='col'>Tax</th><td></td></tr></thead>"
                $(headers).appendTo("#table_gifts")

                $(function() {
                    months = ['Jan. ', 'Feb. ', 'Mar. ', 'Apr. ', 'May. ', 'Jun. ', 'Jul. ', 'Aug. ', 'Sep. ', 'Oct. ', 'Nov. ', 'Dec. ']

                    $("#gifts_table_body").html("")

                    // iterate over the gifts query set.
                    $.each(data, function(i, item) {
                        // get the date.
                        date = item.fields.date;
                        
                        // break the date into year month and day, with the month as letters.
                        year = date.split("-")[0]
                        month = months[parseInt(date.split("-")[1]) - 1]
                        day = date.split("-")[2]
                        
                        tr_style = "<tr>";
                        if (!item.fields.is_gift){
                            tr_style = "<tr id='bootstrap-overrides' class='warningrow'>"
                        }

                        // print each gift as a table row, and append it to the table body.
                        var $tr = $(tr_style).append(
                            $('<th>').text(month + day + ', ' + year),
                            $('<td>').text(item.fields.gift_money),
                            $('<td>').text(item.fields.gift_tax),
                            $('<td>').html('<button data-id="'+ item.pk +'" data-amount="'+ item.fields.gift_money +'" data-tax="'+ item.fields.gift_tax +'" type="submit" class="btn btn-danger btn-delete-gift"><i class="fa fa-trash-alt fa-lg"></i></button>')
                        ).appendTo("#gifts_table_body")
                    });
                });
            }
            
        }
    })
    .fail(function(xhr, status, error){
        var err = eval("(" + xhr.responseText + ")");
            alert(err.Message);
    })
}


/**
 * Sends the gift data to the backend to change the relevant balance row.
 * If successful, it also updates the balance at the toolbar
 * @param {event} e The event that triggered this funciton
 */
function add_balance(e){
    // prevent default event response
    e.preventDefault();
        
    $.ajax({
        url:"/add_balance",
        type:"POST",
        data:{
            is_gift: $("#f_is_gift").is(":checked"),
            date: $("#f_gift_date").val(),
            gift_money: $("#f_gift_money").val(),
            gift_tax: $("#f_gift_tax").val(),
        }
    })
    .done(function(response){
        // get the new dates and set the gifts date to current date.
        set_gifts_date();

        // get the new balance value and update it in the toolbar and in the modal
        balance = parseFloat(response.balance)
        $('#div_user_balance').html("$" + balance)
        $("#balance_modal_title").html("Balance $" + balance)

        // show the new total profit
        $("#total-profit").html("$" + (parseFloat($("#total-profit").html().replace('$', '')) - parseFloat($("#f_gift_tax").val())));

        // on success, reload the gifts table to show the new gifts
        $('#s_filter_gifts_by_date').trigger("change");

        // reset the textboxes
        $("#f_gift_money").val('');
        $("#f_gift_tax").val('');
    })
    .fail(function(xhr, status, error){
        console.log(xhr)
    })
}


/**
 * Gets a gift id to delete and deletes the gift associated with this id.
 */
function delete_gift(){
    id = $(this).data("id")
    gift_amount = $(this).data("amount")
    gift_tax = $(this).data("tax")
    gift_value = gift_amount - gift_tax

    if (confirm("Are you sure you want to delete this gift?")){
        $.ajax({
            url: '/delete_gift',
            type:"POST",
            data:{
                id: id
            }
        })
        .done(function(data){
            // get the new dates and set the gifts date to current date.
            set_gifts_date();

            balance = parseFloat($("#div_user_balance").html().replace('$', '')) - parseFloat(gift_value)
            $('#div_user_balance').html("$" + balance)
            $("#balance_modal_title").html("Balance $" + balance)

            // show the new total profit
            $("#total-profit").html("$" + (parseFloat($("#total-profit").html().replace('$', '')) - parseFloat(gift_tax)))

            // on success, reload the gifts table to show the new gifts
            $('#s_filter_gifts_by_date').trigger("change");
        })
        .fail(function(xhr, status, error){
            var err = eval("(" + xhr.responseText + ")");
                alert(err.Message);
        })
    }
}


/**
 * Using ajax to pass all the parameters needed to create a sale to the backend.
 * @param [{event}] e: The click event that submitted the form.
 */
function add_sale(e){
    
    // prevent the default response after button click
    e.preventDefault();

    $.ajax({
        url:"/add_sale",
        type:"POST",
        data:{
            date: $("#f_date").val(),
            ebay_price: $("#f_ebay_price").val(),
            amazon_price: $("#f_amazon_price").val(),
            ebay_tax: $("#f_ebay_tax").val(),
            paypal_tax: $("#f_paypal_tax").val(),
            tm_fee: $("#f_tm_fee").val(),
            promoted: $("#f_promoted").val(),
            profit: $("#f_profit").val(),
            discount: $("#f_discount").val(),
            country: $("#f_country").val(),
        }
    })
    .done(function(response){
        // on success, if the country is not default, open the hipshipper modal
        if ($("#f_country").val() != '-----'){
            $("#hipshipper_modal").data("reference", response.sale_id)
            $("#hipshipper_modal").modal("toggle");
        }
        else {
            // reload the page if the country is default
            location.reload();
        }
    })
    .fail(function(xhr, status, error){
        var err = eval("(" + xhr.responseText + ")");
            alert(err.Message);
    })
}


/**
 * Gets all the values needed to update a sale and sends it back to the server to process the request.
 * If successful, the balance at the toolbar will update immediately.
 *  @param  {int} id The id of the sale to update
 *  @param  {float} value The new value
 *  @param  {float} lastvalue The previous value
 *  @param  {string} type What has been changed
 */
function update_sale(id, value, lastvalue, type){
    if (type == "country"){
        update_hipshipper(id, lastvalue);
    }
    
    $.ajax({
        url:"/update_sale",
        type:"POST",
        data:{
            id: id, 
            type: type, 
            value: value, 
            lastvalue: lastvalue
        },
    })
    .done(function(response){
        $("#div_user_balance").load(location.href + " #div_user_balance");
    })
    .fail(function(response){
        console.log(response)
    })
}


/**
 * Gets a sale id to delete and deletes the sale associated with this id.
 */
function delete_sale(){
    
    id = $(this).parent("td").data("id");

    if (confirm("Are you sure you want to delete this sale?")){
        $.ajax({
            url: '/delete_sale',
            type:"POST",
            data:{
                id: id
            }
        })
        .done(function(response){
            // when sale successfully deleted, refresh the page to show the changes.
            location.reload();
        })
        .fail(function(xhr, status, error){
            var err = eval("(" + xhr.responseText + ")");
                alert(err.Message);
        })
    }
}


/**
 * Sends the form fields to the backend to add hipshipper to sales from foreign countries.
 * @param {event} e The event that triggered the function
 */
function add_hipshipper(e){

    // prevent default response to event
    e.preventDefault();

    if ($("#hipshipper_modal").data('lastvalue')){
        // That means the hipshipper was edited
        $.ajax({
            url: "/update_hipshipper",
            type: "POST",
            data:{
                sale_id: $("#hipshipper_modal").data('reference'),
                buyer_paid: $("#f_buyer_paid").val(),
                seller_paid: $("#f_seller_paid").val(),
                lastvalue: $("#hipshipper_modal").data('lastvalue')
            },
            success: function(){
                console.log("succesfully updated!")
            }
        })
    }

    $.ajax({
        url:'/add_hipshipper',
        type:'POST',
        data:{
            buyer_paid: $("#f_buyer_paid").val(),
            seller_paid: $("#f_seller_paid").val(),
            sale_entry: $("#hipshipper_modal").data('reference'),
        }
    })
    .done(function(response){
        // if successful, refresh the page
        location.reload();
    })
    .fail(function(xhr){
        console.log(xhr);
    })
}

/**
 * Sends the differences to the server
 */
function update_hipshipper(sale_id, lastvalue){
    
}   


/**
 * Sends the relevant data to the backend to create a new managing cost.
 * @param {event} e The event that triggered the function
 */
function add_cost(e){
    
    // prevent default response to event
    e.preventDefault();

    $.ajax({
        url:"/add_cost",
        type:"POST",
        data:{
            name:$("#f_cost_name").val(),
            value:$("#f_cost_value").val(),
        }
    })
    .done(function(data){
        // clear table contents
        $("#table_costs").html("<tbody id='costs_table_body'></tbody>");
        
        // if data is valid
        if (!data.data){
            // create the table structure
            var headers = "<thead><tr class='headerrow-gift'><th scope='col'>Name</th><th scope='col'>Value</th><th scope='col'></th></tr></thead>"
            $(headers).appendTo("#table_costs")

            $(function() {
                // reset the table body
                $("#costs_table_body").html("")

                $.each(data, function(i, item) {
                    // get the values
                    cost_name = item.fields.name;
                    cost_value = item.fields.value;

                    // insert each cost to the table body
                    var $tr = $('<tr>').append(
                        $('<th>').text(cost_name),
                        $('<td>').text(cost_value),
                        $('<td>').html("<button data-id='" + item.pk + "' type='submit' class='btn btn-danger btn-delete-cost' ><i class='fa fa-trash-alt fa-lg'></i></button>")
                    ).appendTo("#costs_table_body")
                });
            });
        }
    })
    .fail(function(response){
        console.log(response.responseText);
        console.log(response);
    });
}


/**
 * Sends the relevant data to the backend to delete a cost
 * @param {int} item The id of the item that has been clicked
 */
function delete_cost(e){
    
    id = $(this).data("id")

    if (confirm("Are you sure you want to delete this cost?")){
        $.ajax({
            url: '/delete_cost',
            type:"POST",
            data:{
                id: id
            }
        })
        .done(function(data){
            // on success, reload the costs table to show the new costs
            $("#table_costs").load(document.URL + " #table_costs");
        })
        .fail(function(xhr, status, error){
            var err = eval("(" + xhr.responseText + ")");
                alert(err.Message);
        })
    }
}

/**
 * Send data to server on blur event on input-data class users only
 * Revert the <input> to a normal text
 */
function send_to_update_sale(){
    // get the values
    var value = $(this).val();
    var td = $(this).parent("td");
    var lastvalue = (td.data('lastvalue')).replace(/\s+/g,''); // remove spaces
    var type = td.data("type");
    
    // remove the input
    $(this).remove();

    if (type == "country"){
        if (!value){
            // if the user has left the input blank, don't change it.
            value = lastvalue.split('/')[0];
        }

        // open hipshipper modal on country change
        $("#hipshipper_modal").data('reference', td.data("id"));
        $("#hipshipper_modal").data('lastvalue', lastvalue);
        $("#hipshipper_modal").modal("show");
    }

    // give the <td> the new value and make it editable
    td.html(value);
    td.addClass("editable");

    update_sale(td.data("id"), value, lastvalue, type);
}


/**
 * Change the clicked editable <td> to <input>
 */
function change_editable(){
    // get the value
    var value = $(this).text();

    // if it's country the value is only the name of the country
    if ($(this).data("type") == 'country'){
        value = "";
        $(this).find("td").each(function(i){
            value += $.trim($(this).text()) + "/";
        })
    }

    // declare what the input will look like and insert it to the <td> clicked
    var input = "<input type='text' class='input-data form-control' value='" + value.split('/')[0] + "'>";
    if ($(this).attr('data-type') != 'country'){
        input = "<input type='Number' class='input-data form-control' value='" + value + "'>";
    }

    // get the profit of the same row
    var profit = 0.0
    $(this).parent("tr").find("td").each(function(i){
        if (i == PROFIT_INDEX){
            profit = $(this).text()
        }
    })

    // save the last value and the original profit as they will serve us later
    $(this).data("lastvalue", value);
    $(this).data("originalProfit", profit)

    // change the <td> to <input> and focus on it
    $(this).html(input);
    $(this).removeClass("editable");
    $('input', this).focus(function(){$(this).select();});
    $('input', this).focus();
}


/**
 * This function is responsible on the sale return mechanism
 */
function return_sale(){
    tr = $(this).parent("td").parent("tr")

    if (tr.attr('id') == "bootstrap-overrides"){
        // sale is coming back to life
        tr.attr("id", "");

        $.ajax({
            url: "/cancel_return_sale",
            type: "POST",
            data: {
                sale_id: $(this).data('id'),
            },
            success:function(data){
                
                /* // update total profit
                $("#total-profit").html(parseFloat(parseFloat($("#total-profit").text().replace('$', '')) + parseFloat(data.profit)))

                tr.toggleClass('warningrow');
                // reload sales table and sum row
                $("#table_sales").load(location.href + " #table_sales");

                //update balance
                $("#div_user_balance").load(location.href + " #div_user_balance");
                $("#balance_modal_title").load(location.href + " #balance_modal_title");

                sum_sales_table(); */

                location.reload();
            }
        })
        .fail(function(data){
            console.log(data);
        });
    }
    else{
        // sale is being returned
        tr.attr("id", "bootstrap-overrides");

        $.ajax({
            url: "/return_sale",
            type: "POST",
            data: {
                sale_id: $(this).data('id'),
            },
            success:function(data){
                
                /* // update total profit
                $("#total-profit").html(parseFloat(parseFloat($("#total-profit").text().replace('$', '')) - parseFloat(data.profit)))
                
                tr.toggleClass('warningrow');

                // reload sales table and sum row
                $("#table_sales").load(location.href + " #table_sales");

                //update balance
                $("#div_user_balance").load(location.href + " #div_user_balance");
                $("#balance_modal_title").load(location.href + " #balance_modal_title");

                sum_sales_table(); */

                location.reload();
            }
        })
        .fail(function(data){
            console.log(data);
        });
    }
}

/**
 * On click lock or unlock the textbox
 * @param {*} e The event
 */
function paypal_lock_handler(e){
    e.preventDefault();

    console.log($(this).hasClass("bg-success"));

    $.ajax({
        url: "/toggle_paypal_editable",
        type: "POST",
        data: {
            value: $(this).hasClass("bg-success")
        },
        success: function(response){
            console.log(response);
            $(".lock-class").toggleClass("bg-success bg-danger");

            if ($(".lock-class").hasClass("bg-success")){
                // unlocked
                $(".lock-class").html("<i class='fa fa-lock-open fa-lg'></i>")
                paypal_balance_value = $("#div_paypal_balance").html()
                $("#div_paypal_balance").html(`
                 <input type='number' id='txt_paypal_balance' class='form-control editable-paypal-balance'
                 value='` + paypal_balance_value + `' data-lastvalue='` + paypal_balance_value + `' />`)
            }
            else{
                // locked
                $(".lock-class").html("<i class='fa fa-lock fa-lg'></i>")
                lastvalue = $("#txt_paypal_balance").data("lastvalue")
                curvalue = $("#txt_paypal_balance").val()
                
                if (lastvalue != curvalue){
                    console.log(curvalue)
                    $.ajax({
                        url: '/update_paypal_balance',
                        type: 'POST',
                        data: {
                            value: curvalue
                        },
                        success: function(response){
                            console.log(response);
                        }
                    })
                }
                $("#div_paypal_balance").html(curvalue);
                
            }
        }
    })
    
}

function filter_sales(){
    value = $("#s_sales_filter_by_date").val();

    $.ajax({
        url: '/filter_sales',
        type: 'POST',
        data: {
            date: value,
        },
        success: function(d){
            table_string = ""

            sales = []
            returned_sales = []
            hipshipper = []

            $(d).each(function(){
                model = this.model;
                data = this.fields;

                if (model == "core.saleentry"){
                    data["pk"] = this.pk;
                    sales.push(data);
                }
                else if(model == "core.returnedsale") {
                    returned_sales.push(data)
                }
                else{
                    hipshipper.push(data)
                }
            })
            
            returned_pks = []
            $(returned_sales).each(function(){
                returned_pks.push(this.sale)
            })

            $(sales).each(function(){
                if (returned_pks.includes(this.pk)){
                    // sale is returned
                    table_string += "<tr id='bootstrap-overrides' class='warningrow'>"
                }
                else{
                    table_string += "<tr>"
                }

                table_string += "<th class='text-success'>" + this.pk + "</th>";

                table_string += "<th>" + this.date + "</th>";

                table_string += "<td class='editable sumtable' data-id='" + this.pk + "' data-type='ebay_price'>" + parseFloat(this.ebay_price) + "</td>";
                
                table_string += "<td class='editable sumtable' data-id='" + this.pk + "' data-type='amazon_price'>" + parseFloat(this.amazon_price) + "</td>";
                
                table_string += "<td class='editable sumtable' data-id='" + this.pk + "' data-type='ebay_tax'>" + parseFloat(this.ebay_tax) + "</td>";
                
                table_string += "<td class='editable sumtable' data-id='" + this.pk + "' data-type='paypal_tax'>" + parseFloat(this.paypal_tax) + "</td>";
                
                table_string += "<td class='editable sumtable' data-id='" + this.pk + "' data-type='tm_fee'>" + parseFloat(this.tm_fee) + "</td>";
                
                table_string += "<td class='editable sumtable' data-id='" + this.pk + "' data-type='promoted'>" + parseFloat(this.promoted) + "</td>";
                
                table_string += "<td class='sumtable' id='loop' data-id='" + this.pk + "' data-type='profit'>" + parseFloat(this.profit) + "</td>";
                
                table_string += "<td class='editable sumtable' data-id='" + this.pk + "' data-type='discount'>" + parseFloat(this.discount) + "</td>";
                
                table_string += "<td class='editable text-center' data-id='" + this.pk + "' data-type='country'>"
                table_string += "<table style='width: 90%;'>"
                if (this.country == '-----'){
                    table_string += "<tr class='bg-secondary'>"
                }
                else{
                    table_string += "<tr>"
                }
                table_string += "<td class='get-country col-12 text-center' colspan='2'>" + this.country + "</td>"
                table_string += "</tr>"
                table_string += "<tr>"
                temp = this
                $(hipshipper).each(function(){
                    if (this.sale_entry == temp.pk){
                        table_string += "<td class='bg-info text-center text-secondary col-6'>"
                        table_string += "<span>Buyer</span><br /><div id='div_hipshipper_buyer'>" + this.buyer_paid + "</div>"
                        table_string += "</td>"

                        table_string += "<td class='bg-primary text-center col-6'>"
                        table_string += "<span>Seller</span><br /><div id='div_hipshipper_seller'>" + this.seller_paid + "</div>"
                        table_string +="</td>"

                        return false;
                    }
                });
                table_string += "</tr></table></td>"

                table_string += "<td data-id='" + this.pk + "' data-type='submit' class='text-center'>"
                table_string += "<button data-id='" + this.pk + "' type='submit' class='btn btn-warning btn-return-sale'>"
                table_string += "<i class='fa fa-undo-alt fa-lg'></i>"
                table_string += "</button>"
                table_string += "<button data-id='" + this.pk +"' type='submit' class='btn btn-danger btn-delete-sale'>"
                table_string += "<i class='fa fa-trash-alt fa-lg'></i>"
                table_string += "</button>"
                table_string += "</td>"

                table_string += "</tr>"

            })
            $("#table_sales tbody").html(table_string)

            sum_sales_table();

            calc_total_date_profit();

            // sales count
            $("#sales-count").html("Sales: " + parseFloat($("#table_sales > tbody > tr").length - 1));

            // ebay bill updated only on page load
            ebay_bill = parseFloat($("#total_sum_eBay_tax").html()) + parseFloat($("#total_sum_promoted").html())
            $("#ebay-bill").html("eBay Bill: $" + parseFloat(-1*ebay_bill));
        }
    }).fail(function(xhr){
        console.log(xhr);
    })
}

function get_user_preferences(){
    USER_PREFERENCES = {};

    prefs_span = $("#user_preferences").html().split(" | ");
    prefs_span = prefs_span.slice(1, prefs_span.length - 1);

    prefs_span.forEach(function(item){
        p_name = item.split(" = ")[0];
        p_value = item.split(" = ")[1];

        if (p_value == "True") p_value = true;
        else if (p_value == "False") p_value = false;
        else if (!isNaN(Number(p_value))) p_value = Number(p_value);
        USER_PREFERENCES[p_name] = p_value;
    });

    $("#f_default_month").prop("checked", USER_PREFERENCES.default_month);
    $("#f_start_month_day").val(USER_PREFERENCES.start_month_day);
    $("#f_sort_by_date").prop("checked", USER_PREFERENCES.sort_by_date);

    return USER_PREFERENCES;
}


$(document).ready(function(){
    USER_PREFERENCES = get_user_preferences();;

    set_gifts_date();

    // filter sales
    $(document).on('change', "#s_sales_filter_by_date", filter_sales);

    // default month
    if (USER_PREFERENCES.default_month){
        $("#s_sales_filter_by_date").val($('#s_sales_filter_by_date option:last-child').val());
        $("#s_sales_filter_by_date").trigger("change");
    }
    else{
        $("#s_sales_filter_by_date").val("all");
        $("#s_sales_filter_by_date").trigger("change");
    }

    // paypal balance change manually
    $(document).on("click", ".lock-class", paypal_lock_handler);
    $(document).on("keypress", "#txt_paypal_balance", function(e){
        var key = e.which;

        if (key == 13){
            e.preventDefault();
            $(".lock-class").click();
        }
    })
    
    // open and close preferences
    $(document).on('click', "#btn_open_preferences", function(){
        if ($("#mySidenav").width() != 0){
            // close
            $("#mySidenav").width("0");
            $("#main").removeAttr("style");
        }
        else{
            // open
            get_user_preferences();
            $("#mySidenav").width("25%");
            $("#mySidenav").height($(window).height() - $("#main_navbar").height() - parseInt($('html').css('font-size')));
            $("#main").css("margin-left", "25%");
            $("#main").width("73%");
        }
    })
    
    // edit preferences
    $(document).on("change", "#form_preferences input,select", function(e){
        if ($(e.target).is("select")){
            value = $(this).val();
        }
        else {
            value = $(e.target).prop("checked");
        }
        $.ajax({
            url: '/edit_preferences',
            type: 'POST',
            data: {
                element_changed: this.id,
                value: value
            },
            success: function(data){
                // do something when preferences are changed
            }
        })
    });

    // editable tables
    $(document).on("dblclick", ".editable", change_editable)

    $(document).on("blur", ".input-data", send_to_update_sale)

    $(document).on("keypress", ".input-data", function(e){
        var key = e.which;
        if (key == 13){
            $(this).trigger("blur");
        }
    });

    // calc profit live on sale creation
    $(document).on("keyup", '#form_add_sale input', calc_profit_form);

    // submit forms
    $(document).on("submit", '#form_add_sale', add_sale);
    $(document).on("submit", "#form_hipshipper", add_hipshipper);
    $(document).on("submit", '#balance-form', add_balance);
    $(document).on("submit", '#cost-register', add_cost);
    // $(document).on("submit", "#form-generate-report", generate_report);

    // delete models
    $(document).on("click", "#table_costs .btn-delete-cost", delete_cost);
    $(document).on("click", "#table_sales .btn-delete-sale", delete_sale);
    $(document).on("click", '#table_gifts .btn-delete-gift', delete_gift);

    // return sale
    $(document).on('click', "#table_sales .btn-return-sale", return_sale);

    // calc add to balance live on gift creation
    $(document).on("keyup", '.add-gift-form', calc_add_to_balance)
    
    /**
     * Updates the profit in live.
     * @returns nothing when the country is changed
     */
    $(document).on("keyup", ".input-data", function(){

        // get the values
        var td = $(this).parent("td");
        var type = td.data("type");
        if (type == "country"){return;}

        var value = $(this).val();
        if (value == null){ value = 0; }

        var lastvalue = parseFloat(td.data("lastvalue"));
        var profit = parseFloat(td.data("originalProfit"))

        POSITIVE_INDEXES = [0, 7];
        type_index = -1;

        if (type == 'ebay_price') { type_index = 0; }
        else if (type == 'amazon_price') { type_index = 1; }
        else if (type == 'ebay_tax') { type_index = 2; }
        else if (type == 'paypal_tax') { type_index = 3; }
        else if (type == 'tm_fee') { type_index = 4; }
        else if (type == 'promoted') { type_index = 5; }
        else if (type == 'discount') { type_index = 7; }

        // add or subtract the change from profit
        if (POSITIVE_INDEXES.includes(type_index)) profit += (value - lastvalue);
        else profit -= (value - lastvalue);

        // change the profit on live
        td.parent("tr").find("td").each(function(i){
            if (i == PROFIT_INDEX){
                $(this).html((profit));
            }
        }); 

        // if the total profit is grater than 0, show it in green, else show it in red.
        if (profit < 0) $("#total-profit").addClass("bg-danger").removeClass("bg-success");
        else $("#total-profit").addClass("bg-success").removeClass("bg-danger");
        
        // print the total profit
        $("#total-profit").html("$" + parseFloat(profit))
        

    });
});


