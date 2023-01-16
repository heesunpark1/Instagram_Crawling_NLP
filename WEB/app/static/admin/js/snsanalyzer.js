;
(function($, window, document, bb, undefined) {
	'use strict';

	// namespace
	var app = app || {};
	app.ui = app.ui || {};

	app.ui.Main = (function() {
		var _defaults = {
			content: '#content',
			sform: '.settig-form',
			formView: '#content-main',
			resultView1: '.js-result-view1',
			resultView2: '.js-result-view2',
			resultView3: '.js-result-view3',
			resultView4: '.js-result-view4',
			sentiHistoryCont: '.js-senti-history',
			sentiKeywordCont: '.js-senti-keyword',
			predictCont: '.js-predict-data',
			eleMusicPlst: '#el-music-playlist',
			eleSentiHistory: '#el-senti-history',
			eleSentiKeyword: '#el-senti-keyword',
			elPredict: '#el-predict-data',
			loader: '#loader-wrapper',
			// doCrawlUrl: '/api/test/',
			getAnalyzeUrl: '/analyze/',
			doAnalyzeUrl: '/analyze/predict/',
			getMusicPlaylistUrl: '/analyze/playlist/'
        };

		return {
			init: function(container, options) {
				this._options = $.extend(true, _defaults, options);
                this._body = container;

                this.$lstmPieChart = bb.generate({
					"data": {
						"columns": [
						],
						"type": "pie",
						"onclick": function (d, i) { console.log("onclick", d, i); },
						"onover": function (d, i) { console.log("onover", d, i); },
						"onout": function (d, i) { console.log("onout", d, i); }
					},
					"bindto": "#PieChart"
				});

                this.$acoAreaChart = bb.generate({
					"data": {
						"x": "x",
						"columns": [],
						"types": {},
					},
					"zoom": {
						"enabled": true
					},
					"axis": {
						"x": {
							"type": "timeseries",
							"tick": {
								"format": "%Y-%m-%d %H:%m %S" //2017-11-15T09:43:28.000Z
							}
						}
					},
					"bindto": "#AreaChart"
				});

                this._assignedHTMLElements();
                this._initProperties();
                this._attachEvents();
                this._initValidate();
			},
			_assignedHTMLElements: function() {
				this.$content = this._body.find(this._options.content);
				this.$loader = this.$content.find(this._options.loader);
				this.$formView = this.$content.find(this._options.formView);
				this.$sform = this.$formView.find(this._options.sform);
				this.$resultView1 = this.$content.find(this._options.resultView1);
				this.$resultView2 = this.$content.find(this._options.resultView2);
				this.$resultView3 = this.$content.find(this._options.resultView3);
				this.$resultView4 = this.$content.find(this._options.resultView4);
				this.$predictCont = this.$resultView1.find(this._options.predictCont);
				this.$elPredict = this.$predictCont.find(this._options.elPredict);
				this.$sentiHistoryCont = this.$resultView2.find(this._options.sentiHistoryCont);
				this.$eleSentiHistory = this.$resultView2.find(this._options.eleSentiHistory);
				this.$sentiKeywordCont = this.$resultView3.find(this._options.sentiKeywordCont);
				this.$eleMusicPlst = this.$resultView4.find(this._options.eleMusicPlst);
				this.$eleSentiKeyword = this.$sentiKeywordCont.find(this._options.eleSentiKeyword);
				// console.log(this.$resultView)
			},
			_initProperties: function() {
				var _this = this;

				// this.$eleSentiKeyword.hide();
				// this.$eleSentiHistory.parents('table').hide();
				this.$resultView1.hide();
				this.$resultView2.hide();
				this.$resultView3.hide();
				this.$resultView4.hide();
				// this.$resultView.hide();

				$.ajax({
					url : _this._options.getAnalyzeUrl
					, cache : false
					, type : 'GET'
					, data : {}
					, contentType : "application/json; charset=utf-8"
					, dataType: "json"
					, beforeSend : function (xhr) {
						xhr.setRequestHeader ("Accept", 'application/json; indent=4');
					}
				}).fail(function() {
					alert('데이터 통신 중 오류가 발생했습니다.');
				}).done(function(result) {
					if (!result) return;
					console.log(result);
				});
			},
			_attachEvents: function() {
				this.$sform.submit(function(e) { e.preventDefault(); });
			},
			_initValidate: function() {
				if (!this.$sform.size()) return;

				this.$sform.validate({
					onclick : false, onfocusout : false, onkeyup : false, focusInvalid : false
					, rules : {
						instaId : 'required', text : 'required'
					}
					, messages : {
						instaId : { required : '인스타그램 아이디를 선택하세요' },
						text : { required : '감성글을 작성하세요' }
					}
					, errorPlacement: function(error, element) {
						return false;
					}
					, showErrors : $.proxy(this._errorHandle, this)
					, submitHandler : $.proxy(this._sformSubmit, this)
				});
			},
			_errorHandle : function(msgs, errs) {
				if (!errs.length) return;

				alert(errs[0].message);
				$(errs[0].element).trigger('focus');
			},
			_sformSubmit: function(e) {
				var formArray = this.$sform.serializeArray();
				var jsonData = {};
				var _this = this;

				_this.$loader.fadeIn(500);

				for (var i = 0; i < formArray.length; i++){
					jsonData[formArray[i]['name']] = formArray[i]['value'];
				}

				_this.sFormData = jsonData;
				// console.log(jsonData);

				$.ajax({
					url : _this._options.doAnalyzeUrl
					, cache : false
					, type : 'GET'
					, data : jsonData
					, contentType : "application/json; charset=utf-8"
					, dataType: "json"
					, beforeSend : function (xhr) {
						xhr.setRequestHeader ("Accept", 'application/json; indent=4');

						_this.crawlStatus = true;
					}
				}).fail(function() {
					alert('데이터 통신 중 오류가 발생했습니다.');
				}).done(function(result) {
					if (!result) return;

					_this.sentiAnalyzeRes = result
					console.log(_this.sentiAnalyzeRes)

					_this._visualizeML([result['ml'][1], result['ml'][2]]);
					// _this._visualizeHistory(result['history']);
					// _this._visualizeAco(result['sentiKword']);
					// _this._ajaxCallMusic(result['playlist']);

					_this.$loader.fadeOut(1000);
					_this.$resultView1.show();
					// _this.$resultView2.show();
					// _this.$resultView3.show();
				});
			},
			_visualizeML: function(result){
				var _this = this;
				var res = "";
				var chartData = [];

				console.log(result[0]);
				console.log(result[1]);

				for(var i=0;i<result[0].length;i++){
					var feel = result[0][i];

					var percnt = Math.floor((parseFloat(result[1][i])) * 100);
					chartData.push([feel, result[1][i]]);
					res += feel + ": " + percnt + "%\n";
				}

				_this.$lstmPieChart.load({
					columns: chartData
				});

				// _this.$elPredict.html(res);

				// if(_this.crawlStatus === true) {
				// 	this.$resultView.show();
				// 	// setTimeout(function(){ alert('ok'); },3000);
				// 	setTimeout(function(){
				// 		_this._runMonitorLog(true);
				// 		_this._runMonitorCsv(true);
				// 	}, 3000);
                //
				// }else{
				// 	this.$resultView.hide();
				// }
			},
			_visualizeHistory: function(result){
				var _this = this;
				var xAxis = ["x"];
				var data = ["감성"];

				console.log(result);

				for(var i=0;i<result.length;i++) {
					var itsDate = new Date();
					console.log(result[i]['time'].substring(0,4), result[i]['time'].substring(5,7), result[i]['time'].substring(8,10))
					itsDate.setFullYear(result[i]['time'].substring(0,4), result[i]['time'].substring(5,7), result[i]['time'].substring(8,10));
					itsDate.setHours(result[i]['time'].substring(11,13), result[i]['time'].substring(14,16), result[i]['time'].substring(17,19))
					// console.log(itsDate);
					xAxis.push(itsDate);
					data.push(result[i]['score']);

					// 텍스트 삽입
					_this.$eleSentiHistory.append("<tr><th scope='row'>"+result[i]['time']+"</th><td>"+result[i]['sentence']+"</td><td>"+result[i]['score']+"</td></tr>");
                }

                _this.$acoAreaChart.load({
					columns: [xAxis, data]
					// ,types:{"감성": "area-spline"}
				});

                // ["data1", 300, 350, 300, 0, -20, 0]

				// "data1": "area-spline"

				// if(_this.crawlStatus === true) {
				// 	this.$resultView.show();
				// 	// setTimeout(function(){ alert('ok'); },3000);
				// 	setTimeout(function(){
				// 		_this._runMonitorLog(true);
				// 		_this._runMonitorCsv(true);
				// 	}, 3000);
                //
				// }else{
				// 	this.$resultView.hide();
				// }
			},
			_visualizeAco: function(result){
				var _this = this;

				console.log(result);
				var res = "\n";
				for(var i=0;i<result.length;i++){
					res += "'"+result[i][0]+"', "+ result[i][1]+"\n";
				}
				_this.$eleSentiKeyword.text(res).show();

				// for(var i=0;i<result.length;i++) {
				// 	var itsDate = new Date();
				// 	console.log(result[i]['date'].substring(0,4), result[i]['date'].substring(5,7), result[i]['date'].substring(8,10))
				// 	itsDate.setFullYear(result[i]['date'].substring(0,4), result[i]['date'].substring(5,7), result[i]['date'].substring(8,10));
				// 	itsDate.setHours(result[i]['date'].substring(11,13), result[i]['date'].substring(14,16), result[i]['date'].substring(17,19))
				// 	// console.log(itsDate);
				// 	xAxis.push(itsDate);
				// 	data.push(result[i]['score']);
                //
                // }
                // _this.$acoAreaChart.load({
				// 	columns: [xAxis, data]
				// 	// ,types:{"감성": "area-spline"}
				// });
			},
			_ajaxCallMusic: function (result) {
				var _this = this, jsonData = { "musicUrl":result[0] };

				$.ajax({
					url : _this._options.getMusicPlaylistUrl
					, cache : false
					, type : 'GET'
					, data : jsonData
					, contentType : "application/json; charset=utf-8"
					, dataType: "json"
					, beforeSend : function (xhr) {
						xhr.setRequestHeader ("Accept", 'application/json; indent=4');

						_this.crawlStatus = true;
					}
				}).fail(function() {
					alert('데이터 통신 중 오류가 발생했습니다.');
				}).done(function(result) {
					if (!result) return;

					_this.musicPlayList = result;
					console.log(_this.musicPlayList);

					_this._visualizeMusic(result['songs']);
					_this.$resultView4.show();
				});
            },
			_visualizeMusic: function (result) {
				var _this = this;

				for(var i=0;i<result.length;i++) {
					// 텍스트 삽입
					_this.$eleMusicPlst.append("<tr><th scope='row'>"+result[i]['title']+"</th><td>"+result[i]['artist']+"</td><td>"+result[i]['albumtitle']+"</td></tr>");
                }

            }
		};
	})();

	$(function() {
		var body = $('body');

		app.ui.Main.init(body, {
			'test':'test'
		});
	});
})(django.jQuery, window, document, bb);