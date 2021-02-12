/* 
    Global Functions
    sum_sales_table: adding a sum row in the end of sales table
    calc_profit: calculating the profit on creation and outputs to #f_profit
    calc_add_to_balance: changing #txt_balance_add to amount of gift - tax
    set_gifts_date(): set the gifts date select to today's date, if not possible show nothing
    delete_sale(item): AJAX - delete sale (item -> the element clicked)
    filter_gifts_by_date(e): AJAX - filter gifts by selected date (e -> event)
    update_sale(id, value, type): AJAX - update sale (id -> clicked sale, value -> new value to assign, type -> the field)
    add_sale(e): AJAX - add sale (e -> event)
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
    $(result).each(function(){
        $('#table_sales').find("tr:last").prev().append('<th>'+ this.toFixed(2) +'</th>')
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
            $("#table_sales").load(location.href + " #table_sales");
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
        $("#table_sales").load(document.URL + " #table_sales");
        sum_sales_table();
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

$(document).ready(function(){
    //set gifts select date and show the relevant data
    set_gifts_date();
    $('#s_filter_gifts_by_date').trigger("change");

    // create total column
    sum_sales_table();

    // change data clicked to input
    $(document).on("dblclick", ".editable", function(){
        var value = $(this).text();
        var input = "<input type='text' class='input-data form-control' value='" + value + "'>";
        if ($(this).attr('data-type') != 'country'){
            input = "<input type='Number' class='input-data form-control' value='" + value + "'>";
        }
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
            value = "-----"
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
                value = "-----"
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

        positive_indexes = [0, 7];
        negative_indexes = [1, 2, 3, 4, 5];
        profit_index = 6;

        if (type == 'ebay_price'){ positive_indexes.splice(0, 1); }
        else if (type == 'amazon_price'){ negative_indexes.splice(0, 1); }
        else if (type == 'ebay_tax'){ negative_indexes.splice(1, 1); }
        else if (type == 'paypal_tax'){ negative_indexes.splice(2, 1); }
        else if (type == 'tm_fee'){ negative_indexes.splice(3, 1); }
        else if (type == 'promoted'){ negative_indexes.splice(4, 1); }
        else if (type == 'discount'){ positive_indexes.splice(1, 1); }

        var profit = 0.0;

        td.parent("tr").find("td").each(function(i){
            if (positive_indexes.includes(i)){
                profit += parseFloat($(this).html());
            }
            else if (negative_indexes.includes(i)){
                profit -= parseFloat($(this).html());
            }
            else if (i != 6 && i != 8 && i != 9){
                if (type != 'ebay_price' && type != 'discount'){
                    profit -= parseFloat(value);
                }
                else{
                    profit += parseFloat(value);
                }
            }
        });

        td.parent("tr").find("td").each(function(i){
            if (i == 6){
                $(this).html((profit.toFixed(2)).toString());
            }
        });

        
    });
});


