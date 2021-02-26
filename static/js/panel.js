// Globals
PROFIT_INDEX = 6;


/**
 * Adds a sum row at the end of the sales table.
 */
function sum_sales_table() {

    var result = [];
    
    // iterate over each row and find all the numbers that are needed to sum up.
    $('#table_sales tr').each(function(){
        $('td.sumtable', this).each(function(index, val){
            // sum up the numbers and give in to result array.
            if(!result[index]) result[index] = 0;
            result[index] += parseFloat($(val).text());
        });
    });
    
    // create and design the sum row
    $('#table_sales').find("tr:last").prev().after('<tr id="bootstrap-overrides" class="greenrow"></tr>');
    $('#table_sales').find("tr:last").prev().append('<th class="align-middle"><i class="fa fa-hashtag fa-md"></i></th>');
    $('#table_sales').find("tr:last").prev().append('<th>Total</th>');

    // print the sum row numbers
    $(result).each(function(i){
        if (i == PROFIT_INDEX){
            $('#table_sales').find("tr:last").prev().append('<th id="total_sum_profit">'+ this.toFixed(2) +'</th>')
        }
        else{
            $('#table_sales').find("tr:last").prev().append('<th>'+ this.toFixed(2) +'</th>')
        }
        
    });

    // fill out blank columns
    $('#table_sales').find("tr:last").prev().append('<th></th>')
    $('#table_sales').find("tr:last").prev().append('<th></th>')
}


/**
 * Calculates the profit from the form inputs and prints it in the profit input.
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
            // calculate and round the total to 2 digits after the decimal.
            total = parseFloat(profit) - parseFloat(costs) - parseFloat(gifts_tax)
            total = Math.round((total + Number.EPSILON) * 100) / 100

            // if the total profit is grater than 0, show it in green, else show it in red.
            if (total < 0) $("#total-profit").addClass("bg-danger") 
            else $("#total-profit").addClass("bg-success")

            // print the total profit
            $("#total-profit").html("$" + total)
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
                var headers = "<thead><tr class='headerrow-gift'><th scope='col'>Date</th><th scope='col'>Gift Amount</th><th scope='col'>Tax</th></tr></thead>"
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

                        // print each gift as a table row, and append it to the table body.
                        var $tr = $('<tr>').append(
                            $('<th>').text(month + day + ', ' + year),
                            $('<td>').text(item.fields.gift_money),
                            $('<td>').text(item.fields.gift_tax)
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
            date: $("#f_gift_date").val(),
            gift_money: $("#f_gift_money").val(),
            gift_tax: $("#f_gift_tax").val(),
        }
    })
    .done(function(response){
        // get the new dates and set the gifts date to current date.
        set_gifts_date();
        
        // get the new balance value and update it in the toolbar and in the modal
        balance = Math.round((parseFloat(response.balance) + Number.EPSILON) * 100) / 100
        $('#div_user_balance').html("$" + balance)
        $("#balance_modal_title").html("Balance $" + balance)

        // show the new total profit
        $("#total-profit").html("$" + (parseFloat($("#total-profit").html().replace('$', '')) - parseFloat($("#f_gift_tax").val())))
    })
    .fail(function(xhr, status, error){
        console.log(xhr)
    })
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
 * @param  {int} item The sale id that has been clicked
 */
function delete_sale(item){
    
    id = $(item).parent("td").data("id");

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
    .fail(function(xhr, status, error){
        var err = eval("(" + xhr.responseText + ")");
            alert(err.Message);
    })
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
                        $('<td>').html("<button data-id='" + item.pk + "' type='submit' class='btn btn-danger btn-delete-sale' onclick='delete_cost(this)' ><i class='fa fa-trash-alt fa-lg'></i></button>")
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
function delete_cost(item){
    
    id = $(item).data("id")

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
    var lastvalue = td.data('lastvalue');
    var type = td.data("type");
    
    // remove the input
    $(this).remove();

    if (type == "country"){
        if (!value){
            // if the user has left the input blank, don't change it.
            value = lastvalue;
        }

        // open hipshipper modal on country change
        $("#hipshipper_modal").data('reference', td.data("id"));
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
        $(this).find("table").find("tr").each(function(i){
            if (i == 0){
                value = $.trim($(this).find("td").text());
            }
        })
    }

    // declare what the input will look like and insert it to the <td> clicked
    var input = "<input type='text' class='input-data form-control' value='" + value + "'>";
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



$(document).ready(function(){
    
    set_gifts_date();

    sum_sales_table();

    calc_total_date_profit();
    
    $(document).on("dblclick", ".editable", change_editable)

    $(document).on("blur", ".input-data", send_to_update_sale)

    $(document).on("keypress", ".input-data", function(e){
        var key = e.which;
        if (key == 13){
            send_to_update_sale();
        }
    });


    $(document).on("keyup", '.form-add-sale', calc_profit_form)

    $(document).on("submit", '#form_add_sale', add_sale)

    $(document).on("submit", "#form_hipshipper", add_hipshipper)

    $(document).on("submit", '#balance-form', add_balance)
    /**
     * Updates the profit in live.
     * @returns nothing when the country is changed
     */
    $(document).on("keyup", ".input-data", function(){

        // get the values
        var type = td.data("type");
        if (type == "country"){return;}

        var value = $(this).val();
        if (value == null){ value = 0; }

        var td = $(this).parent("td");
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
                $(this).html((profit.toFixed(2)).toString());
            }
        });

        
    });
});


