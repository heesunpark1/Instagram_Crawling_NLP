;
(function($, window, document, undefined) {
	'use strict';

	// namespace
	var app = app || {};
	app.ui = app.ui || {};

	app.ui.Main = (function() {
		var _defaults = {
			content: '.content',
			sform: '.settig-form',
			formView: '.js-form-view',
			resultView: '.js-result-view',
			monitorCont: '.js-monitor-log',
			csvCont: '.js-csv-data',
			eleMonitor: '#el-log-monitor',
			elCsv: '#el-csv-data',
			// doCrawlUrl: '/api/test/',
			getCrawlUrl: '/crawl/',
			doCrawlUrl: '/crawl/save/',
			doMonitorLogUrl: '/crawl/monitor/log/',
			doMonitorCsvUrl: '/crawl/monitor/csvdata/'
        };

		return {
			init: function(container, options) {
				this._options = $.extend(true, _defaults, options);
                this._body = container;

                this._assignedHTMLElements();
                this._initProperties();
                this._attachEvents();
                this._initValidate();
			},
			_assignedHTMLElements: function() {
				this.$content = this._body.find(this._options.content);
				this.$formView = this.$content.find(this._options.formView);
				this.$sform = this.$formView.find(this._options.sform);

				this.$resultView = this.$content.find(this._options.resultView);
				this.$monitorCont = this.$resultView.find(this._options.monitorCont);
				this.$eleMonitor = this.$monitorCont.find(this._options.eleMonitor);
				this.$csvCont = this.$resultView.find(this._options.csvCont);
				this.$eleCsv = this.$csvCont.find(this._options.elCsv);

				// console.log(this.$resultView)
			},
			_initProperties: function() {
				var _this = this;

				this.$resultView.hide();

				$.ajax({
					url : _this._options.getCrawlUrl
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
						sns_kind : 'required'
					}
					, messages : {
						sns_kind : { required : 'SNS를 선택하세요' }
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

				for (var i = 0; i < formArray.length; i++){
					jsonData[formArray[i]['name']] = formArray[i]['value'];
				}

				_this.sFormData = jsonData;
				// console.log(jsonData);

				// jsonData['username'] = 'admin';
				// jsonData['password'] = 'wlsrhkd2';

				$.ajax({
					url : _this._options.doCrawlUrl
					, cache : false
					, type : 'GET'
					, data : jsonData
					, contentType : "application/json; charset=utf-8"
					, dataType: "json"
					, beforeSend : function (xhr) {
						xhr.setRequestHeader ("Accept", 'application/json; indent=4');

						_this.crawlStatus = true;
						_this._visualizeMonitor();
					}
				}).fail(function() {
					alert('데이터 통신 중 오류가 발생했습니다.');
				}).done(function(result) {
					if (!result) return;
					// console.log(result);

				});

				// e.submit();
			},
			_visualizeMonitor: function(){
				var _this = this;

				if(_this.crawlStatus === true) {
					this.$resultView.show();
					// setTimeout(function(){ alert('ok'); },3000);
					setTimeout(function(){
						_this._runMonitorLog(true);
						_this._runMonitorCsv(true);
					}, 3000);

				}else{
					this.$resultView.hide();
				}
			},
			_runMonitorLog: function(isFirst, startNum){
				var _this = this;

				var jsonData = {
					'env': _this.sFormData.env
				};

				if(!isFirst) jsonData['startNum'] = startNum;

				$.ajax({
					url : _this._options.doMonitorLogUrl
					, cache : false
					, type : 'GET'
					, data : jsonData
					, contentType : "application/json; charset=utf-8"
					, dataType: "json"
					, beforeSend : function (xhr) {
						xhr.setRequestHeader ("Accept", 'application/json; indent=4');


					}
				}).fail(function() {
					alert('데이터 통신 중 오류가 발생했습니다.');
				}).done(function(result) {
					if (!result) return;
					// console.log(result);
					if(isFirst){
						for(var i=0;i<result.log.lines.length;i++){
							// console.log(result.log.lines[i]);
							_this.$eleMonitor.append(result.log.lines[i].text).show();
						}
					} else {
						for(var i=0;i<result.log.lines.length;i++){
							if(result.log.lines[i].num > startNum) _this.$eleMonitor.append(result.log.lines[i].text).show();
						}
					}
					_this.$eleMonitor.scrollTop(_this.$eleMonitor[0].scrollHeight);

					// setTimeout($.proxy(_this._runMonitorLog(false, result.log.endNum), _this), 2000);
					setTimeout(function(){
						_this._runMonitorLog(false, result.log.endNum);
					}, 2000);
				});
			},
			_runMonitorCsv: function(isFirst, startNum) {
				var _this = this;

				var jsonData = {
					'sns_kind': _this.sFormData.sns_kind
				};

				if(!isFirst) jsonData['startNum'] = startNum;

				$.ajax({
					url : _this._options.doMonitorCsvUrl
					, cache : false
					, type : 'GET'
					, data : jsonData
					, contentType : "application/json; charset=utf-8"
					, dataType: "json"
					, beforeSend : function (xhr) {
						xhr.setRequestHeader ("Accept", 'application/json; indent=4');


					}
				}).fail(function() {
					alert('데이터 통신 중 오류가 발생했습니다.');
				}).done(function(result) {
					if (!result) return;
					// console.log(result);
					if(isFirst){
						for(var i=0;i<result.csv.lines.length;i++){
							// console.log(result.csv.lines[i]);
							_this.$eleCsv.append(result.csv.lines[i].text).show();
						}
					} else {
						for(var i=0;i<result.csv.lines.length;i++){
							if(result.csv.lines[i].num > startNum) _this.$eleCsv.append(result.csv.lines[i].text).show();
						}
					}
					_this.$eleCsv.scrollTop(_this.$eleCsv[0].scrollHeight);

					setTimeout(function(){
						_this._runMonitorCsv(false, result.csv.endNum);
					}, 2000);
				});
            }
		};
	})();

	$(function() {
		var body = $('body');
		app.ui.Main.init(body, {
			'test':'test'
		});
	});
})(jQuery, window, document);