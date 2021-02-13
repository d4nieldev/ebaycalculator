/* 
    Global Functions
    sum_sales_table(): adding a sum row in the end of sales table
    calc_profit(): calculating the profit on creation and outputs to #f_profit
    calc_add_to_balance(): changing #txt_balance_add to amount of gift - tax
    calc_total_date_profit(): calculating the total profit of the selected date
    set_gifts_date(): set the gifts date select to today's date, if not possible show nothing
    delete_sale(item): AJAX - delete sale (item -> the element clicked)
    filter_gifts_by_date(e): AJAX - filter gifts by selected date (e -> event)
    update_sale(id, value, type): AJAX - update sale (id -> clicked sale, value -> new value to assign, type -> the field)
    add_sale(e): AJAX - add sale (e -> event)
    add_balance(e): AJAX - adding gifts to balance (e -> event)
    add_cost(e): AJAX - add cost (e -> event)
    delete_cost(e): AJAX - delete cost (e -> event)
*/
function sum_sales_table(){
    
    var result = [];
    $('#table_sales tr').each(function(){
        $('td.sumtable', this).each(function(index, val){
            if(!result[index]) result[index] = 0;
            result[index] += parseFloat($(val).text());
        });
    });
    
    $('#table_sales').find("tr:last").prev().after('<tr id="bootstrap-overrides" class="greenrow"></tr>');
    $('#table_sales').find("tr:last").prev().append('<th>Total</th>')
    $(result).each(function(i){
        $('#table_sales').find("tr:last").prev().append('<th>'+ this.toFixed(2) +'</th>')
        if (i == 6){
            $('#table_sales').find("tr:last").prev().append('<th id="total_sum_profit">'+ this.toFixed(2) +'</th>')
        }
        
    });
    $('#table_sales').find("tr:last").prev().append('<th></th>')
    $('#table_sales').find("tr:last").prev().append('<th></th>')
}

function calc_profit() {
    ebay_price = $('#f_ebay_price').val();
    amazon_price = $('#f_amazon_price').val();
    ebay_tax = $('#f_ebay_tax').val();
    paypal_tax = $('#f_paypal_tax').val();
    tm_fee = $('#f_tm_fee').val();
    promoted = $('#f_promoted').val();
    discount = $("#f_discount").val();

    $("#f_profit").val(ebay_price - amazon_price - ebay_tax - paypal_tax - tm_fee - promoted + discount);
}

function calc_add_to_balance() {
    gift_money = $('#f_gift_money').val();
    gift_tax = $('#f_gift_tax').val();
    $('#txt_balance_add').val(gift_money - gift_tax);
}

function calc_total_date_profit(){
    profit = $("#total_sum_profit").text();
    costs = 0;
    $("#total-profit span").each(function(){
        costs += parseFloat($(this).text());
    });
    total = profit - costs
    $("#total-profit").html("Month Profit: " + Math.round((total + Number.EPSILON) * 100) / 100)
}

function set_gifts_date(){
    var today = new Date();
    year = today.getFullYear();
    month = today.getMonth() + 1;

    $("#s_filter_gifts_by_date option").each(function(){
        if ($(this).val() == year + '-' + month){
            $("#s_filter_gifts_by_date").val($(this).val());
        }
    })
    
}

function delete_sale(item){
    id = $(item).parent("td").data("id")
    if (confirm("Are you sure you want to delete this sale?")){
        $.ajax({
            url: '/delete_sale',
            type:"POST",
            data:{id:id}
        })
        .done(function(response){
            location.reload();
        })
        .fail(function(xhr, status, error){
            var err = eval("(" + xhr.responseText + ")");
                alert(err.Message);
        })
    }
}

function filter_gifts_by_date(e){
    e.preventDefault();
    $.ajax({
        url: "/filter_gifts",
        type: "GET",
        data: {date:$("#s_filter_gifts_by_date").val()},
        success:function(data){
            // clear table contents
            $("#table_gifts").html("<tbody id='gifts_table_body'></tbody>");
            
            // selected month and year
            if (!data.data){
                var headers = "<thead><tr class='headerrow-gift'><th scope='col'>Date</th><th scope='col'>Gift Amount</th><th scope='col'>Tax</th></tr></thead>"
                $(headers).appendTo("#table_gifts")

                $(function() {
                    months = ['Jan. ', 'Feb. ', 'Mar. ', 'Apr. ', 'May. ', 'Jun. ', 'Jul. ', 'Aug. ', 'Sep. ', 'Oct. ', 'Nov. ', 'Dec. ']
                $("#gifts_table_body").html("")
                $.each(data, function(i, item) {
                    date = item.fields.date;
                    year = date.split("-")[0]
                    month = months[parseInt(date.split("-")[1]) - 1]
                    day = date.split("-")[2]
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

function update_sale(id, value, type){
    $.ajax({
        url:"/update_sale",
        type:"POST",
        data:{id:id, type:type, value:value},
    })
    .done(function(response){
        $("#div_user_balance").load(location.href + " #div_user_balance");
    })
    .fail(function(response){
        console.log(response)
    })
}

function add_sale(e){
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
        if ($("#f_country").val() != '-----'){
            $("#hipshipper_modal").data("reference", response.sale_id)
            $("#hipshipper_modal").modal("toggle");
        }
        else {
            location.reload();
        }
    })
    .fail(function(xhr, status, error){
        var err = eval("(" + xhr.responseText + ")");
            alert(err.Message);
    })
}

function add_hipshipper(e){
    e.preventDefault();
    console.log("reference " + $("#hipshipper_modal").data('reference'))
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
        console.log(response)
        location.reload();
    })
    .fail(function(xhr, status, error){
        var err = eval("(" + xhr.responseText + ")");
            alert(err.Message);
    })
}

function add_balance(e){
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
        set_gifts_date();
        $('#s_filter_gifts_by_date').trigger("change");
        balance = response.balance
        $('#div_user_balance').html("" + Math.round((balance + Number.EPSILON) * 100) / 100)
        $("#balance_modal_title").html("Balance $" + Math.round((balance + Number.EPSILON) * 100) / 100)
    })
    .fail(function(xhr, status, error){
        var err = eval("(" + xhr.responseText + ")");
            alert(err.Message);
    })
}

function add_cost(e){
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
            var headers = "<thead><tr class='headerrow-gift'><th scope='col'>Name</th><th scope='col'>Value</th><th scope='col'></th></tr></thead>"
            $(headers).appendTo("#table_costs")

            $(function() {
                $("#costs_table_body").html("")
                $.each(data, function(i, item) {
                    cost_name = item.fields.name;
                    cost_value = item.fields.value;
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


function delete_cost(item){
    id = $(item).data("id")
    if (confirm("Are you sure you want to delete this cost?")){
        $.ajax({
            url: '/delete_cost',
            type:"POST",
            data:{id:id}
        })
        .done(function(data){
            $("#table_costs").load(document.URL + " #table_costs");
        })
        .fail(function(xhr, status, error){
            var err = eval("(" + xhr.responseText + ")");
                alert(err.Message);
        })
    }
}

$(document).ready(function(){
    //set gifts select date and show the relevant data
    set_gifts_date();
    $('#s_filter_gifts_by_date').trigger("change");

    // create total column
    sum_sales_table();

    calc_total_date_profit();

    // change data clicked to input
    $(document).on("dblclick", ".editable", function(){
        var value = $(this).text();
        if ($(this).data("type") == 'country'){
            $(this).find("table").find("tr").each(function(i){
                if (i == 0){
                    value = $(this).find("td").text().replace(/\s/g, '');
                }
            })
        }
        var input = "<input type='text' class='input-data form-control' value='" + value + "'>";
        if ($(this).attr('data-type') != 'country'){
            input = "<input type='Number' class='input-data form-control' value='" + value + "'>";
        }
        profit = 0.0
        $(this).parent("tr").find("td").each(function(i){
            if (i == 6){
                profit = $(this).text()
            }
        })

        $(this).data("lastvalue", value);
        $(this).data("originalProfit", profit)

        $(this).html(input);
        $(this).removeClass("editable");
        $('input', this).focus(function(){$(this).select();});
        $('input', this).focus();
    });

    // on blur save data
    $(document).on("blur", ".input-data", function(){
        var value = $(this).val();
        var td = $(this).parent("td");
        var type = td.data("type");
        $(this).remove();
        if (type == "country" && !value) {
            value = "-----";
        }
        if (type == "country"){
            $("#hipshipper_modal").data('reference', td.data("id"));
            $("#hipshipper_modal").modal("show");
        }
        td.html(value);
        td.addClass("editable");
        update_sale(td.data("id"), value, type);
    });

    // on key press save data
    $(document).on("keypress", ".input-data", function(e){
        var key = e.which;
        if (key == 13){
            var value = $(this).val();
            var td = $(this).parent("td");
            var type = td.data("type");
            $(this).remove();
            if (type == "country" && !value) {
                value = "-----";
            }
            if (type == "country"){
                $("#hipshipper_modal").data('reference', td.data("id"));
                $("#hipshipper_modal").modal("show");
            }
            td.html(value);
            td.addClass("editable");
            update_sale(td.data("id"), value, type);
        }
    });

    // on key up update profit
    $(document).on("keyup", ".input-data", function(){
        var value = $(this).val();
        if (value == null){ value = 0; }
        var td = $(this).parent("td");
        var type = td.data("type");
        var lastvalue = parseFloat(td.data("lastvalue"));

        positive_indexes = [0, 7];
        negative_indexes = [1, 2, 3, 4, 5];
        type_index = -1;
        profit_index = 6;

        if (type == 'ebay_price'){ type_index = 0; }
        else if (type == 'amazon_price'){ type_index = 1; }
        else if (type == 'ebay_tax'){ type_index = 2; }
        else if (type == 'paypal_tax'){ type_index = 3; }
        else if (type == 'tm_fee'){ type_index = 4; }
        else if (type == 'promoted'){ type_index = 5; }
        else if (type == 'discount'){ type_index = 7; }

        var profit = parseFloat(td.data("originalProfit"))

        if (positive_indexes.includes(type_index)){
            profit += (value - lastvalue);
        }
        else{
            profit -= (value - lastvalue);
        }

        td.parent("tr").find("td").each(function(i){
            if (i == 6){
                $(this).html((profit.toFixed(2)).toString());
            }
        });

        
    });
});


