odoo.define('AccountingDashboard.AccountingDashboard', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');
    var _t = core._t;
    var QWeb = core.qweb;
    var self = this;
    var currency;
    var ActionMenu = AbstractAction.extend({

        template: 'Invoicedashboard',


        events: {
            'click .invoice_dashboard': 'onclick_dashboard',
            'click #prog_bar': 'onclick_prog_bar',
            'change #toggle-two': 'onclick_toggle_two',

        },

        renderElement: function (ev) {
            var self = this;
            $.when(this._super())
                .then(function (ev) {


                    $('#toggle-two').bootstrapToggle({
                        on: 'View All Entries',
                        off: 'View Posted Entries'
                    });


                    var posted = false;
                    if ($('#toggle-two')[0].checked == true) {
                        posted = "posted"
                    }


                    rpc.query({
                        model: "account.move",
                        method: "get_currency",
                    })
                        .then(function (result) {
                            currency = result;

                        })

                    var arg = 'last_month'
                    rpc.query({
                        model: 'account.move',
                        method: 'get_pie_month_target',
                        args: [posted],
                    })
                        .then(function (result) {

                            $(document).ready(function () {
                                var options = {
                                    // legend: false,
                                    responsive: true,
                                    legend: {
                                        position: 'bottom'
                                    }
                                };
                                if (window.donuts != undefined)
                                    window.donuts.destroy();
                                window.donuts = new Chart($("#horizontalbarChart"), {
                                    type: 'pie',
                                    tooltipFillColor: "rgba(51, 51, 51, 0.55)",
                                    data: {
                                        labels: result.days,
                                        datasets: [{
                                            data: result.totalamount,
                                            backgroundColor: [
                                                '#66aecf ', '#6993d6 ', '#666fcf', '#7c66cf', '#9c66cf',
                                                '#bc66cf ', '#b75fcc', ' #cb5fbf ', ' #cc5f7f ', ' #cc6260',
                                                '#cc815f', '#cca15f ', '#ccc25f', '#b9cf66', '#99cf66',
                                                ' #75cb5f ', '#60cc6c', '#804D8000', '#80B33300', '#80CC80CC', '#f2552c', '#00cccc',
                                                '#1f2e2e', '#993333', '#00cca3', '#1a1a00', '#3399ff',
                                                '#8066664D', '#80991AFF', '#808E666FF', '#804DB3FF', '#801AB399',
                                                '#80E666B3', '#8033991A', '#80CC9999', '#80B3B31A', '#8000E680',
                                                '#804D8066', '#80809980', '#80E6FF80', '#801AFF33', '#80999933',
                                                '#80FF3380', '#80CCCC00', '#8066E64D', '#804D80CC', '#809900B3',
                                                '#80E64D66', '#804DB380', '#80FF4D4D', '#8099E6E6', '#806666FF'
                                            ],
                                            hoverBackgroundColor: [
                                                '#66aecf ', '#6993d6 ', '#666fcf', '#7c66cf', '#9c66cf',
                                                '#bc66cf ', '#b75fcc', ' #cb5fbf ', ' #cc5f7f ', ' #cc6260',
                                                '#cc815f', '#cca15f ', '#ccc25f', '#b9cf66', '#99cf66',
                                                ' #75cb5f ', '#60cc6c', '#804D8000', '#80B33300', '#80CC80CC', '#f2552c', '#00cccc',
                                                '#1f2e2e', '#993333', '#00cca3', '#1a1a00', '#3399ff',
                                                '#8066664D', '#80991AFF', '#808E666FF', '#804DB3FF', '#801AB399',
                                                '#80E666B3', '#8033991A', '#80CC9999', '#80B3B31A', '#8000E680',
                                                '#804D8066', '#80809980', '#80E6FF80', '#801AFF33', '#80999933',
                                                '#80FF3380', '#80CCCC00', '#8066E64D', '#804D80CC', '#809900B3',
                                                '#80E64D66', '#804DB380', '#80FF4D4D', '#8099E6E6', '#806666FF'
                                            ]
                                        }]
                                    },
                                    legend: {
              display: true,
              position: "bottom",
              labels: {
                fontColor: "#333",
                fontSize: 16
              }
            },
                                    options: {
                                        responsive: false
                                    }
                                });
                            });
                        })
                    rpc.query({
                        model: "account.move",
                        method: "get_overdues",

                    }).then(function (result) {
                            var due_count = 0;
                            _.forEach(result, function (x) {
                                due_count++;
                                $('#overdues').append('<li><a class="overdue_line_cust" href="#" id="line_' + x.parent + '" data-user-id="' + x.parent + '">' + x.due_partner + '</a>' + '&nbsp;&nbsp;&nbsp;&nbsp;' + '<span>' + x.due_amount + ' ' + currency + '</span>' + '</li>');

                                //                                $('#overdues_amounts').append('<li><a class="overdue_line_cust" href="#" id="line_' + x.parent + '" data-user-id="' + x.parent + '">' + x.amount + '</a>' + '<span>'+' '+currency+ '</span>' + '</li>' );

                            });

                            $('#due_count').append('<span class="badge badge-danger">' + due_count + ' Due(s)</span>');
                        })
                    var f = 'this_month'
                    rpc.query({
                        model: "account.move",
                        method: "get_top_10_customers_month",
                        args: [posted,f]
                    }).then(function (result) {
                            var due_count = 0;
                            var amount;
                            _.forEach(result, function (x) {
                                $('#top_10_customers_this_month').show();
                                due_count++;
                                amount = self.format_currency(currency, x.amount);
                                $('#top_10_customers_this_month').append('<li><div id="line_' + x.parent + '" data-user-id="' + x.parent + '">' + x.customers + '</div>' + '<div id="line_' + x.parent + '" data-user-id="' + x.parent + '">' + amount + '</div>' + '</li>');

                            });
                        })
                    rpc.query({
                        model: "account.move",
                        method: "bank_balance",
                        args: [posted]
                    })
                        .then(function (result) {
                            var banks = result['banks'];
                            var amount;
                            var balance = result['banking'];
                            for (var k = 0; k < banks.length; k++) {
                                amount = self.format_currency(currency, balance[k]);
                                //                                $('#charts').append('<li><a ' + banks[k] + '" data-user-id="' + banks[k] + '">' + banks[k] + '</a>'+  '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + '<span>'+ balance[k] +'</span>' + '</li>' );
                                $('#current_bank_balance').append('<li><div>' + banks[k] + '</div><div>' + amount + '</div></li>');
                                //                                $('#current_bank_balance').append('<li>' + banks[k] +'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+ balance[k] +  '</li>' );
                                $('#drop_charts_balance').append('<li>' + balance[k].toFixed(2) + '</li>');
                            }
                        })



                     rpc.query({
                        model: "account.move",
                        method: "total_crm_rpt1",
                        args: [posted],
                    })
                        .then(function (result) {

                            var tot_crm_rpt1_amt = result['totalamt'];
                            var day_crm_rpt1 = result['daystr'];
                            var date_crm_rpt1 = result['datestr'];
                            var daily_target_rpt1 = result['daily_target'];
                            var daily_achpercent_rpt1 = result['achpercent'];
                            var daily_balance_rpt1 = result['balance']; //daily_target_rpt1-tot_crm_rpt1_amt;

                            //tot_crm_rpt1_amt = self.format_currency(currency, tot_crm_rpt1_amt);
                            //daily_target_rpt1 = self.format_currency(currency, daily_target_rpt1);
                            //daily_balance_rpt1 = self.format_currency(currency, daily_balance_rpt1);

                            $('#scr_day_crm_rpt1').append('<span>' + day_crm_rpt1 + '</span>')
                            $('#scr_date_crm_rpt1').append('<span>' + date_crm_rpt1 + '</span>')
                            $('#scr_total_crm_rpt1').append('<span>' + tot_crm_rpt1_amt + ' AED</span><div class="title">Achieved</div>')
                            $('#scr_target_rpt1').append('<span>' + daily_target_rpt1 + ' AED</span><div class="title">Target</div>')
                            $('#scr_arcpercent_rpt1').append('<span>' + daily_achpercent_rpt1 + '</span><div class="title"></div>')
                            $('#scr_balance_rpt1').append('<span> Balance : ' + daily_balance_rpt1 + ' AED</span>')
                            //                            $('#unreconciled_counts_this_year').append('<span style= "color:#455e7b;">' + unreconciled_counts_this_year + ' Item(s)</span><div class="title">This Year</div>')
                        })

                     rpc.query({
                        model: "account.move",
                        method: "total_crm_rpt2",
                        args: [posted],
                    })
                        .then(function (result) {

                            var tot_crm_rpt2_amt = result['totalamt'];
                            var day_crm_rpt2 = result['daystr'];
                            var date_crm_rpt2 = result['datestr'];
                            var daily_target_rpt2 = result['daily_target'];
                            var daily_achpercent_rpt2 = result['achpercent'];
                            var daily_balance_rpt2 = result['balance']; //daily_target_rpt2-tot_crm_rpt2_amt;

                            //tot_crm_rpt2_amt = self.format_currency(currency, tot_crm_rpt2_amt);
                            //daily_target_rpt2 = self.format_currency(currency, daily_target_rpt2);
                            //daily_balance_rpt2 = self.format_currency(currency, daily_balance_rpt2);

                            $('#scr_day_crm_rpt2').append('<span>' + day_crm_rpt2 + '</span>')
                            $('#scr_date_crm_rpt2').append('<span>' + date_crm_rpt2 + '</span>')
                            $('#scr_total_crm_rpt2').append('<span>' + tot_crm_rpt2_amt + ' AED</span><div class="title">Achieved</div>')
                            $('#scr_target_rpt2').append('<span>' + daily_target_rpt2 + ' AED</span><div class="title">Target</div>')
                            $('#scr_arcpercent_rpt2').append('<span>' + daily_achpercent_rpt2 + '</span><div class="title"></div>')
                            $('#scr_balance_rpt2').append('<span> Balance : ' + daily_balance_rpt2 + ' AED</span>')
                            //                            $('#unreconciled_counts_this_year').append('<span style= "color:#455e7b;">' + unreconciled_counts_this_year + ' Item(s)</span><div class="title">This Year</div>')
                        })

                     rpc.query({
                        model: "account.move",
                        method: "total_crm_pie_summary",
                        args: [posted],
                    })
                        .then(function (result) {

                            var total_month_amt = result['totalamt'];
                             var total_month_target = result['targetamt'];
                             var total_month_balance = result['balance'];

                            //total_month_amt = self.format_currency(currency, total_month_amt);
                            //total_month_target = self.format_currency(currency, total_month_target);
                            //total_month_balance = self.format_currency(currency, total_month_balance);

                            $('#scr_this_month_achieved').append('<span>Achieved : ' + total_month_amt + ' AED</span>')
                            $('#scr_this_month_target').append('<span>Target : ' + total_month_target + ' AED</span>')
                            $('#scr_this_month_balance').append('<span>Balance : ' + total_month_balance + ' AED</span>')
                            //                            $('#unreconciled_counts_this_year').append('<span style= "color:#455e7b;">' + unreconciled_counts_this_year + ' Item(s)</span><div class="title">This Year</div>')
                        })

                    rpc.query({
                        model: "account.move",
                        method: "total_crm_pie_summary_today",
                        args: [posted],
                    })
                        .then(function (result) {

                            var total_month_amt = result['totalamt'];
                             var total_month_target = result['targetamt'];
                             var total_month_balance = result['balance'];

                            //total_month_amt = self.format_currency(currency, total_month_amt);
                            //total_month_target = self.format_currency(currency, total_month_target);
                            //total_month_balance = self.format_currency(currency, total_month_balance);

                            $('#scr_today_achieved').append('<span>Achieved : ' + total_month_amt + ' AED</span>')
                            $('#scr_today_target').append('<span>Target : ' + total_month_target + ' AED</span>')
                            $('#scr_today_balance').append('<span>Balance : ' + total_month_balance + ' AED</span>')
                            //                            $('#unreconciled_counts_this_year').append('<span style= "color:#455e7b;">' + unreconciled_counts_this_year + ' Item(s)</span><div class="title">This Year</div>')
                        })

                    rpc.query({
                        model: "account.move",
                        method: "get_current_month_asofnow_prodata",
                        args: [posted],
                    })
                        .then(function (result) {

                            var totalamount = result['totalamount'];
                             var targetasofnow = result['targetasofnow'];
                             var balance = result['balance'];
                             var asofnowdays = result['balance'];


                            ///totalamount = String(totalamount) + ' AED'//self.format_currency(currency, totalamount);
                            //targetasofnow = //self.format_currency(currency, targetasofnow);
                           // balance = self.format_currency(currency, balance);

                            $('#scr_asofnow_budget').append('<span>Target : ' + String(targetasofnow )+ ' AED</span>')
                            $('#scr_asofnow_achieved').append('<span> Achieved : ' + String(totalamount) + ' AED</span>')
                            $('#scr_asofnowbalance').append('<span>Balance : ' + String(balance) + ' AED</span>')
                            //                            $('#unreconciled_counts_this_year').append('<span style= "color:#455e7b;">' + unreconciled_counts_this_year + ' Item(s)</span><div class="title">This Year</div>')
                        })

                     rpc.query({
                        model: "account.move",
                        method: "total_crm_rpt3",
                        args: [posted],
                    })
                        .then(function (result) {

                            var tot_crm_rpt3_amt = result['totalamt'];
                            var day_crm_rpt3 = result['daystr'];
                            var date_crm_rpt3 = result['datestr'];
                            var daily_target_rpt3 = result['daily_target'];
                            var daily_achpercent_rpt3 = result['achpercent'];
                            var daily_balance_rpt3 = result['balance']; //daily_target_rpt3-tot_crm_rpt3_amt;

                            tot_crm_rpt3_amt = String(tot_crm_rpt3_amt) //+' AED' //self.format_currency(currency, tot_crm_rpt3_amt);
                            daily_target_rpt3 = String(daily_target_rpt3) //+' AED' // self.format_currency(currency, daily_target_rpt3);
                            daily_balance_rpt3 = String(daily_balance_rpt3) //+' AED' //self.format_currency(currency, daily_balance_rpt3);

                            $('#scr_day_crm_rpt3').append('<span>' + day_crm_rpt3 + '</span>')
                            $('#scr_date_crm_rpt3').append('<span>' + date_crm_rpt3 + '</span>')
                            $('#scr_total_crm_rpt3').append('<span>' + String(tot_crm_rpt3_amt) + ' AED</span><div class="title">Achieved</div>')
                            $('#scr_target_rpt3').append('<span>' + String(daily_target_rpt3) + ' AED</span><div class="title">Target</div>')
                            $('#scr_arcpercent_rpt3').append('<span>' + daily_achpercent_rpt3 + '</span><div class="title"></div>')
                            $('#scr_balance_rpt3').append('<span> Balance : ' + String(daily_balance_rpt3) + ' AED</span><div class="title"></div>')
                            //                            $('#unreconciled_counts_this_year').append('<span style= "color:#455e7b;">' + unreconciled_counts_this_year + ' Item(s)</span><div class="title">This Year</div>')
                        })
                    rpc.query({
                        model: "account.move",
                        method: "total_crm_rpt4",
                        args: [posted],
                    })
                        .then(function (result) {

                            var tot_crm_rpt4_amt = result['totalamt'];
                            var day_crm_rpt4 = result['daystr'];
                            var date_crm_rpt4 = result['datestr'];
                            var daily_target_rpt4 = result['daily_target'];
                            var daily_achpercent_rpt4 = result['achpercent'];
                            var daily_balance_rpt4 = result['balance']; //daily_target_rpt4-tot_crm_rpt4_amt;

                            tot_crm_rpt4_amt = String(tot_crm_rpt4_amt) + ' AED'//self.format_currency(currency, tot_crm_rpt4_amt);
                            daily_target_rpt4 = String(daily_target_rpt4) + ' AED'//self.format_currency(currency, daily_target_rpt4);
                            daily_balance_rpt4 = String(daily_balance_rpt4) + ' AED'//self.format_currency(currency, daily_balance_rpt4);

                            $('#scr_day_crm_rpt4').append('<span>' + day_crm_rpt4 + '</span>')
                            $('#scr_date_crm_rpt4').append('<span>' + date_crm_rpt4 + '</span>')
                            $('#scr_total_crm_rpt4').append('<span>' + tot_crm_rpt4_amt + '</span><div class="title">Achieved</div>')
                            $('#scr_target_rpt4').append('<span>' + daily_target_rpt4 + '</span><div class="title">Target</div>')
                            $('#scr_arcpercent_rpt4').append('<span>' + daily_achpercent_rpt4 + '</span><div class="title"></div>')
                            $('#scr_balance_rpt4').append('<span> Balance : ' + daily_balance_rpt4 + '</span>')
                            //                            $('#unreconciled_counts_this_year').append('<span style= "color:#455e7b;">' + unreconciled_counts_this_year + ' Item(s)</span><div class="title">This Year</div>')
                        })

                     rpc.query({
                        model: "account.move",
                        method: "total_crm_rpt7",
                        args: [posted],
                    })
                        .then(function (result) {

                            var tot_crm_rpt7_amt = result['totalamt'];
                            var day_crm_rpt7 = result['daystr'];
                            var date_crm_rpt7 = result['datestr'];
                            var daily_target_rpt7 = result['daily_target'];
                            var daily_achpercent_rpt7 = result['achpercent'];
                            var daily_balance_rpt7 = result['balance']; //daily_target_rpt7-tot_crm_rpt7_amt;

                            tot_crm_rpt7_amt = String(tot_crm_rpt7_amt) + ' AED'//self.format_currency(currency, tot_crm_rpt7_amt);
                            daily_target_rpt7 = String(daily_target_rpt7) + ' AED'//self.format_currency(currency, daily_target_rpt7);
                            daily_balance_rpt7 = String(daily_balance_rpt7) + ' AED'//self.format_currency(currency, daily_balance_rpt7);

                            $('#scr_day_crm_rpt7').append('<span>' + day_crm_rpt7 + '</span>')
                            $('#scr_date_crm_rpt7').append('<span>' + date_crm_rpt7 + '</span>')
                            $('#scr_total_crm_rpt7').append('<span>' + tot_crm_rpt7_amt + '</span><div class="title">Achieved</div>')
                            $('#scr_target_rpt7').append('<span>' + daily_target_rpt7 + '</span><div class="title">Target</div>')
                            $('#scr_arcpercent_rpt7').append('<span>' + daily_achpercent_rpt7 + '</span><div class="title"></div>')
                            $('#scr_balance_rpt7').append('<span> Balance : ' + daily_balance_rpt7 + '</span>')
                            //                            $('#unreconciled_counts_this_year').append('<span style= "color:#455e7b;">' + unreconciled_counts_this_year + ' Item(s)</span><div class="title">This Year</div>')
                        })

                     rpc.query({
                        model: "account.move",
                        method: "total_crm_rpt5",
                        args: [posted],
                    })
                        .then(function (result) {

                            var tot_crm_rpt5_amt = result['totalamt'];
                            var day_crm_rpt5 = result['daystr'];
                            var date_crm_rpt5 = result['datestr'];
                            var daily_target_rpt5 = result['daily_target'];
                            var daily_achpercent_rpt5 = result['achpercent'];
                            var daily_balance_rpt5 = result['balance']; //daily_target_rpt5-tot_crm_rpt5_amt;

                            tot_crm_rpt5_amt = String(tot_crm_rpt5_amt) + ' AED'//self.format_currency(currency, tot_crm_rpt5_amt);
                            daily_target_rpt5 = String(daily_target_rpt5) + ' AED'//self.format_currency(currency, daily_target_rpt5);
                            daily_balance_rpt5 = String(daily_balance_rpt5) + ' AED'//self.format_currency(currency, daily_balance_rpt5);

                            $('#scr_day_crm_rpt5').append('<span>' + day_crm_rpt5 + '</span>')
                            $('#scr_date_crm_rpt5').append('<span>' + date_crm_rpt5 + '</span>')
                            $('#scr_total_crm_rpt5').append('<span>' + tot_crm_rpt5_amt + '</span><div class="title">Achieved</div>')
                            $('#scr_target_rpt5').append('<span>' + daily_target_rpt5 + '</span><div class="title">Target</div>')
                            $('#scr_arcpercent_rpt5').append('<span>' + daily_achpercent_rpt5 + '</span><div class="title"></div>')
                            $('#scr_balance_rpt5').append('<span> Balance : ' + daily_balance_rpt5 + '</span>')
                            //                            $('#unreconciled_counts_this_year').append('<span style= "color:#455e7b;">' + unreconciled_counts_this_year + ' Item(s)</span><div class="title">This Year</div>')
                        })

                     rpc.query({
                        model: "account.move",
                        method: "total_crm_rpt6",
                        args: [posted],
                    })
                        .then(function (result) {

                            var tot_crm_rpt6_amt = result['totalamt'];
                            var day_crm_rpt6 = result['daystr'];
                            var date_crm_rpt6 = result['datestr'];
                            var daily_target_rpt6 = result['daily_target'];
                            var daily_achpercent_rpt6 = result['achpercent'];
                            var daily_balance_rpt6 = result['balance']; //daily_target_rpt6-tot_crm_rpt6_amt;

                            tot_crm_rpt6_amt = String(tot_crm_rpt6_amt) + ' AED'//self.format_currency(currency, tot_crm_rpt6_amt);
                            daily_target_rpt6 = String(daily_target_rpt6) + ' AED'//self.format_currency(currency, daily_target_rpt6);
                            daily_balance_rpt6 = String(daily_balance_rpt6) + ' AED'//self.format_currency(currency, daily_balance_rpt6);

                            $('#scr_day_crm_rpt6').append('<span>' + day_crm_rpt6 + '</span>')
                            $('#scr_date_crm_rpt6').append('<span>' + date_crm_rpt6 + '</span>')
                            $('#scr_total_crm_rpt6').append('<span>' + tot_crm_rpt6_amt + '</span><div class="title">Achieved</div>')
                            $('#scr_target_rpt6').append('<span>' + daily_target_rpt6 + '</span><div class="title">Target</div>')
                            $('#scr_balance_rpt6').append('<span> Balance : ' + daily_balance_rpt6 + '</span>')
                            //                            $('#unreconciled_counts_this_year').append('<span style= "color:#455e7b;">' + unreconciled_counts_this_year + ' Item(s)</span><div class="title">This Year</div>')
                        })


                    rpc.query({
                        model: "account.move",
                        method: "total_crm_weekly",
                        args: [posted]
                    })
                        .then(function (result) {
                           var datestr = result['datestr'];
                            var daystr = result['daystr'];
                            var amount;
                            var totalamt = result['totalamt'];
                            for (var k = 0; k < datestr.length; k++) {
                                amount = String(amount) + ' AED'//self.format_currency(currency, totalamt[k]);
                                //                                $('#charts').append('<li><a ' + banks[k] + '" data-user-id="' + banks[k] + '">' + banks[k] + '</a>'+  '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + '<span>'+ balance[k] +'</span>' + '</li>' );
                                //$('#fixed_deposit_list').append('<li><div>' + depositname[k] + '</div><div>' + amount + '</div></li>');
                                $('#total_crm_weekly').append('<li><div>' + datestr[k] + '</div><div>' + amount + '</div></li>');
                                //                                $('#current_bank_balance').append('<li>' + banks[k] +'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+ balance[k] +  '</li>' );
                                //$('#drop_charts_balance').append('<li>' + depositamount[k].toFixed(2) + '</li>');
                            }
                        })


                    rpc.query({
                        model: "account.move",
                        method: "get_latebills",

                    }).then(function (result) {
                            var late_count = 0;

                            _.forEach(result, function (x) {
                                late_count++;
                                $('#latebills').append('<li><a class="overdue_line_cust" href="#" id="line_' + x.parent + '" data-user-id="' + x.parent + '">' + x.partner + '<span>' + x.amount + ' ' + currency + '</span>' + '</a>' + '</li>');
                            });
                            $('#late_count').append('<span class="badge badge-danger">' + late_count + ' Late(s)</span>');
                        })
                    rpc.query({
                        model: "account.move",
                        method: "get_total_invoice",
                    })
                        .then(function (result) {
                            var total_invoice = result[0].sum;
                            total_invoice = total_invoice
                            $('#total_invoice').append('<span>' + total_invoice + ' ' + currency + '</span> ')
                        })
                    rpc.query({
                        model: "account.move",
                        method: "get_total_invoice_this_month",
                        args: [posted],
                    })
                        .then(function (result) {
                            var invoice_this_month = result[0].sum;
                            if (invoice_this_month) {
                                var total_invoices_this_month = invoice_this_month.toFixed(2)
                                $('#total_invoices_').append('<span>' + total_invoices_this_month + ' ' + currency + '</span> <div class="title">This month</div>')
                            }
                        })

                    rpc.query({
                        model: "account.move",
                        method: "get_total_invoice_last_month",
                    })
                        .then(function (result) {
                            var invoice_last_month = result[0].sum;
                            var total_invoices_last_month = invoice_last_month
                            $('#total_invoices_last').append('<span>' + total_invoices_last_month + ' ' + currency + '</span><div class="title">Last month</div>')
                        })

                    rpc.query({
                        model: "account.move",
                        method: "unreconcile_items"
                    })
                        .then(function (result) {

                            var unreconciled_count = result[0].count;

                            $('#unreconciled_items').append('<span>' + unreconciled_count + ' Item(s)</a></span> ')
                        })
                    rpc.query({
                        model: "account.move",
                        method: "unreconcile_items_this_month",
                        args: [posted],
                    })
                        .then(function (result) {
                            var unreconciled_counts_ = result[0].count;
                            $('#unreconciled_items_').append('<span>' + unreconciled_counts_ + ' Item(s)</span><div class="title">This month</div>')
                        })
                    rpc.query({
                        model: "account.move",
                        method: "unreconcile_items_this_year",
                        args: [posted],
                    })
                        .then(function (result) {

                            var unreconciled_counts_this_year = result[0].count;

                            $('#unreconciled_counts_this_year').append('<span>' + unreconciled_counts_this_year + '  Item(s)</span><div class="title">This Year</div>')
                            //                            $('#unreconciled_counts_this_year').append('<span style= "color:#455e7b;">' + unreconciled_counts_this_year + ' Item(s)</span><div class="title">This Year</div>')
                        })

                    rpc.query({
                        model: "account.move",
                        method: "unreconcile_items_last_year"
                    })
                        .then(function (result) {
                            var unreconciled_counts_last_year = result[0].count;

                            $('#unreconciled_counts_last_year').append('<span>' + unreconciled_counts_last_year + '  Item(s)</span><div class="title">Last Year</div>')

                        })
                    rpc.query({
                        model: "account.move",
                        method: "month_income"
                    })
                        .then(function (result) {
                            var income = result[0].debit - result[0].credit;
                            income = -income;
                            income = self.format_currency(currency, income);
                            $('#total_income').append('<span>' + income + '</span>')
                        })
                    rpc.query({
                        model: "account.move",
                        method: "month_income_this_month",
                        args: [posted],
                    })
                        .then(function (result) {
                            var incomes_ = result[0].debit - result[0].credit;
                            if (incomes_) {
                                incomes_ = -incomes_;
                                incomes_ = self.format_currency(currency, incomes_);
                                $('#total_incomes_').append('<span>' + incomes_ + '</span><div class="title">This month</div>')

                            } else {
                                incomes_ = -incomes_;
                                incomes_ = self.format_currency(currency, incomes_);
                                $('#total_incomes_').append('<span>' + incomes_ + '</span><div class="title">This month</div>')
                            }
                        })

                    rpc.query({
                        model: "account.move",
                        method: "month_income_last_month"
                    })
                        .then(function (result) {
                            var incomes_last = result[0].debit - result[0].credit;
                            incomes_last = -incomes_last;
                            incomes_last = self.format_currency(currency, incomes_last);
                            $('#total_incomes_last').append('<span>' + incomes_last + '</span><div class="title">Last month</div>')
                        })

                     rpc.query({
                        model: "account.move",
                        method: "total_bank_balance",
                        args: [posted],
                    })
                        .then(function (result) {

                            var tot_bank_balance = result[0].totalbalance;
                            tot_bank_balance = self.format_currency(currency, tot_bank_balance);

                            $('#total_bank_balance').append('<span>' + tot_bank_balance + '</span>')
                            //                            $('#unreconciled_counts_this_year').append('<span style= "color:#455e7b;">' + unreconciled_counts_this_year + ' Item(s)</span><div class="title">This Year</div>')
                        })



                       rpc.query({
                        model: "account.move",
                        method: "total_share_profit",
                        args: [posted],
                    })
                        .then(function (result) {

                            var totalshareprofit = result[0].amount;
                            totalshareprofit = self.format_currency(currency, totalshareprofit);

                            $('#totalshareprofit').append('<span>' + totalshareprofit + '</span>')
                            //                            $('#unreconciled_counts_this_year').append('<span style= "color:#455e7b;">' + unreconciled_counts_this_year + ' Item(s)</span><div class="title">This Year</div>')
                        })





                        rpc.query({
                        model: "account.move",
                        method: "total_fixeddeposit_profit",
                        args: [posted],
                    })
                        .then(function (result) {

                            var totalfixeddeposit = result[0].amount;
                            totalfixeddeposit = self.format_currency(currency, totalfixeddeposit);

                            $('#totalfixeddeposit').append('<span>' + totalfixeddeposit + '</span>')
                            //                            $('#unreconciled_counts_this_year').append('<span style= "color:#455e7b;">' + unreconciled_counts_this_year + ' Item(s)</span><div class="title">This Year</div>')
                        })

                        rpc.query({
                        model: "account.move",
                        method: "fixed_deposit_list",
                        args: [posted]
                    })
                        .then(function (result) {
                            var depositname = result['depositname'];
                            var amount;
                            var depositamount = result['depositamount'];
                            for (var k = 0; k < depositname.length; k++) {
                                amount = self.format_currency(currency, depositamount[k]);
                                //                                $('#charts').append('<li><a ' + banks[k] + '" data-user-id="' + banks[k] + '">' + banks[k] + '</a>'+  '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + '<span>'+ balance[k] +'</span>' + '</li>' );
                                //$('#fixed_deposit_list').append('<li><div>' + depositname[k] + '</div><div>' + amount + '</div></li>');
                                $('#fixed_deposit_list').append('<li><div>' + depositname[k] + '</div><div>' + amount + '</div></li>');
                                //                                $('#current_bank_balance').append('<li>' + banks[k] +'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+ balance[k] +  '</li>' );
                                //$('#drop_charts_balance').append('<li>' + depositamount[k].toFixed(2) + '</li>');
                            }
                        })

                        rpc.query({
                        model: "account.move",
                        method: "crm_sales_list",
                        args: [posted]
                    })
                        .then(function (result) {
                            var agentname = result['agentname'];
                            //var dates = result['dates'];
                            var today_amt = result['today_amt'];
                            var thismonth = result['thismonth'];
                            var amount_thismonth;
                            var amount_today;
                            //var salesamount = result['salesamount'];
                            $('#crm_sales_list').append('<li><div>Name</div><div>This Month Amt</div><div>Today Amt</div></li>');
                            for (var k = 0; k < thismonth.length; k++) {
                                amount_thismonth = self.format_currency(currency, thismonth[k]);
                                amount_today = self.format_currency(currency, today_amt[k]);
                                //                                $('#charts').append('<li><a ' + banks[k] + '" data-user-id="' + banks[k] + '">' + banks[k] + '</a>'+  '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + '<span>'+ balance[k] +'</span>' + '</li>' );
                                //$('#fixed_deposit_list').append('<li><div>' + depositname[k] + '</div><div>' + amount + '</div></li>');
                                $('#crm_sales_list').append('<li><div>' + agentname[k] + '</div><div align="right">' + amount_thismonth + '</div><div align="right">' + amount_today + '</div></li>');
                                //                                $('#current_bank_balance').append('<li>' + banks[k] +'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+ balance[k] +  '</li>' );
                                //$('#drop_charts_balance').append('<li>' + depositamount[k].toFixed(2) + '</li>');
                            }
                        })


                         rpc.query({
                        model: "account.move",
                        method: "current_month_achievement_list",
                        args: [posted]
                    })
                        .then(function (result) {
                            var account_name = result['account_name'];
                            var budget_amt = result['budget_amt'];
                            var arch_amt = result['arch_amt'];
                            var budget_amt_thismonth;
                            var arch_amt_thismonth;
                            $('#current_month_achievement_list').append('<li><div>Account</div><div>Budget</div><div>Achieved</div></li>');
                            for (var k = 0; k < budget_amt.length; k++) {
                                budget_amt_thismonth = self.format_currency(currency, budget_amt[k]);
                                arch_amt_thismonth = self.format_currency(currency, arch_amt[k]);
                                $('#current_month_achievement_list').append('<li><div>' + account_name[k] + '</div><div align="right">' + budget_amt_thismonth + '</div><div align="right">' + arch_amt_thismonth + '</div></li>');
                            }
                        })



                    rpc.query({
                        model: "account.move",
                        method: "month_expense"
                    })
                        .then(function (result) {
                            var expense = result[0].debit - result[0].credit;
                            var expenses = expense;
                            expenses = self.format_currency(currency, expenses);
                            $('#total_expense').append('<span>' + expenses + '</span>')
                        })
                    rpc.query({
                        model: "account.move",
                        method: "month_expense_this_month",
                        args: [posted],
                    }).then(function (result) {
                            var expense_this_month = result[0].debit - result[0].credit;
                            if (expense_this_month) {

                                var expenses_this_month_ = expense_this_month;
                                expenses_this_month_ = self.format_currency(currency, expenses_this_month_);
                                $('#total_expenses_').append('<span>' + expenses_this_month_ + '</span><div class="title">This month</div>')
                            } else {
                                var expenses_this_month_ = expense_this_month;
                                expenses_this_month_ = self.format_currency(currency, expenses_this_month_);
                                $('#total_expenses_').append('<span>' + expenses_this_month_ + '</span><div class="title">This month</div>')

                            }
                        })
                    rpc.query({
                        model: "account.move",
                        method: "month_expense_this_year",
                        args: [posted],
                    }).then(function (result) {
                            var expense_this_year = result[0].debit - result[0].credit;
                            if (expense_this_year) {

                                var expenses_this_year_ = expense_this_year;
                                expenses_this_year_ = self.format_currency(currency, expenses_this_year_);
                                $('#total_expense_this_year').append('<span >' + expenses_this_year_ + '</span><div class="title">This Year</div>')
                            } else {
                                var expenses_this_year_ = expense_this_year;
                                expenses_this_year_ = self.format_currency(currency, expenses_this_year_);
                                $('#total_expense_this_year').append('<span >' + expenses_this_year_ + '</span><div class="title">This Year</div>')
                            }
                        })
                    rpc.query({
                        model: "account.move",
                        method: "month_income_last_year"
                    })
                        .then(function (result) {
                            var incomes_last_year = result[0].debit - result[0].credit;
                            incomes_last_year = -incomes_last_year
                            incomes_last_year = self.format_currency(currency, incomes_last_year);
                            $('#total_incomes_last_year').append('<span>' + incomes_last_year + '</span><div class="title">Last Year</div>')
                        })
                    rpc.query({
                        model: "account.move",
                        method: "month_income_this_year",
                        args: [posted],
                    })
                        .then(function (result) {
                            var incomes_this_year = result[0].debit - result[0].credit;
                            if (incomes_this_year) {
                                incomes_this_year = -incomes_this_year;
                                incomes_this_year = self.format_currency(currency, incomes_this_year);
                                $('#total_incomes_this_year').append('<span>' + incomes_this_year + '</span><div class="title">This Year</div>')
                            } else {
                                incomes_this_year = -incomes_this_year;
                                incomes_this_year = self.format_currency(currency, incomes_this_year);
                                $('#total_incomes_this_year').append('<span>' + incomes_this_year + '</span><div class="title">This Year</div>')
                            }

                        })

                    rpc.query({
                        model: "account.move",
                        method: "profit_income_this_month",
                        args: [posted],
                    }).then(function (result) {
                            var net_profit = true
                            if (result[1] == undefined) {
                                result[1] = 0;
                                if ((result[0]) > (result[1])) {
                                    net_profit = -result[1] + result[0]
                                }

                            }

                            if (result[0] == undefined) {

                                result[0] = 0;
                            }

                            if ((-result[1]) > (result[0])) {
                                net_profit = -result[1] + result[0]
                            } else if ((result[1]) > (result[0])) {
                                net_profit = -result[1] + result[0]
                            } else {
                                net_profit = -result[1] + result[0]
                            }
                            var profit_this_months = net_profit;
                            if (profit_this_months) {
                                var net_profit_this_months = profit_this_months;
                                net_profit_this_months = self.format_currency(currency, net_profit_this_months);
                                $('#net_profit_this_months').empty();
                                $('#net_profit_this_months').append('<div class="title">Net Profit/Loss &nbsp;&nbsp;&nbsp;</div><span>' + net_profit_this_months + '</span>')
                                $('#net_profit_current_months').append('<span>' + net_profit_this_months + '</span> <div class="title">This Month</div>')

                            } else {
                                var net_profit_this_months = profit_this_months;
                                net_profit_this_months = self.format_currency(currency, net_profit_this_months);
                                $('#net_profit_this_months').empty();
                                $('#net_profit_this_months').append('<div class="title">Net Profit/Loss &nbsp;&nbsp;&nbsp;</div><span>' + net_profit_this_months + '</span>')
                                $('#net_profit_current_months').append('<span>' + net_profit_this_months + '</span> <div class="title">This Month</div>')
                            }
                        })
				                        rpc.query({
                        model: "account.move",
                        method: "total_salary_income",
                        args: [posted],
                    })
                        .then(function (result) {

                            var totalsalary = result[0].amount;
                            totalsalary = self.format_currency(currency, totalsalary);

                            $('#totalsalary').append('<span>' + totalsalary + '</span>')
                            //                            $('#unreconciled_counts_this_year').append('<span style= "color:#455e7b;">' + unreconciled_counts_this_year + ' Item(s)</span><div class="title">This Year</div>')
                        })

                   rpc.query({
                        model: "account.move",
                        method: "salary_list",
                        args: [posted]
                    }).then(function (result) {
                            var due_count = 0;
                            var amount;
                            _.forEach(result, function (x) {
                                $('#salary_list').show();
                                due_count++;
                                amount = self.format_currency(currency, x.salaryamount);
                                $('#salary_list').append('<li><div id="line_' + x.parent + '" data-user-id="' + x.parent + '">' + x.partner + '</div>' + '<div id="line_' + x.parent + '" data-user-id="' + x.parent + '">' + amount + '</div>' + '</li>');

                            });
                        })	

                    rpc.query({
                        model: "account.move",
                        method: "profit_income_this_year",
                        args: [posted],
                    })
                        .then(function (result) {
                            var net_profit = true


                            if (result[1] == undefined) {
                                result[1] = 0;
                                if ((result[0]) > (result[1])) {
                                    net_profit = result[1] - result[0]
                                }

                            }

                            if (result[0] == undefined) {

                                result[0] = 0;
                            }

                            if ((-result[1]) > (result[0])) {
                                net_profit = -result[1] + result[0]
                            } else if ((result[1]) > (result[0])) {
                                net_profit = -result[1] + result[0]
                            } else {
                                net_profit = -result[1] + result[0]
                            }
                            var profit_this_year = net_profit;
                            if (profit_this_year) {
                                var net_profit_this_year = profit_this_year;
                                net_profit_this_year = self.format_currency(currency, net_profit_this_year);
                                $('#net_profit_this_year').empty();
                                $('#net_profit_this_year').append('<div class="title">Net Profit/Loss &nbsp;&nbsp;&nbsp;</div><span>' + net_profit_this_year + '</span>')
                                $('#net_profit_current_year').append('<span>' + net_profit_this_year + '</span> <div class="title">This Year</div>')
                            } else {
                                var net_profit_this_year = profit_this_year;
                                net_profit_this_year = self.format_currency(currency, net_profit_this_year);
                                $('#net_profit_this_year').empty();
                                $('#net_profit_this_year').append('<div class="title">Net Profit/Loss &nbsp;&nbsp;&nbsp;</div><span>' + net_profit_this_year + '</span>')
                                $('#net_profit_current_year').append('<span>' + net_profit_this_year + '</span> <div class="title">This Year</div>')

                            }
                        })
                });
        },

        format_currency: function(currency, amount){
             if (typeof(amount) != 'number'){
                amount = parseFloat(amount);
             }
             var formatted_value = (parseInt(amount)).toLocaleString(currency.language, {minimumFractionDigits: 2})
             if (currency.position === "after") {
                return formatted_value += ' ' + currency.symbol;
             } else {
                return currency.symbol + ' ' + formatted_value;
             }
        },

        willStart: function () {
            var self = this;
            self.drpdn_show = false;
            return Promise.all([ajax.loadLibs(this), this._super()]);
        },
    });
    core.action_registry.add('invoice_dashboard', ActionMenu);

});