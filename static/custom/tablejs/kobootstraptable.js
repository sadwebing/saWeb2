//添加ko自定义绑定
ko.bindingHandlers.myBootstrapTable = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
        //这里的oParam就是绑定的viewmodel
        var oViewModel = valueAccessor();
        var $ele = $(element).bootstrapTable(oViewModel.params);
        //给viewmodel添加bootstrapTable方法
        oViewModel.bootstrapTable = function () {
            return $ele.bootstrapTable.apply($ele, arguments);
        }
    },
    update: function (element, valueAccessor, allBindingsAccessor, viewModel) {}
};

//初始化
(function ($) {
    //向ko里面新增一个bootstrapTableViewModel方法
    ko.bootstrapTableViewModel = function (options) {
        var that = this;

        this.default = {
            striped: true,
            cache: false,
            pagination: true,
            sortable: true,
            sortOrder: "asc",
            pageNumber: 1,
            pageSize: 15,
            pageList: [15, 50, 100, 'ALL'],
            search: true,
            uniqueId: "id",
            showColumns: true,
            showRefresh: true,
            minimumCountColumns: 2,
            clickToSelect: true,
            showToggle: true,
            cardView: false,
            detailView: false,
        };
        this.params = $.extend({}, this.default, options || {});
        //this.params = function (data){
        //    this.params = $.extend({}, this.default, options || data);
        //}

        //得到选中的记录
        this.getSelections = function () {
            var arrRes = that.bootstrapTable("getSelections")
            return arrRes;
        };
        //刷新
        this.refresh = function (params) {
            if (params){
                that.bootstrapTable("refresh", params);
            }else {that.bootstrapTable("refresh");}
        };
        this.destroy = function () {
            that.bootstrapTable("destroy");
        };
        this.getOptions = function () {
            var arrRes = that.bootstrapTable("getOptions");
            return arrRes;
        };
        this.removeAll = function () {
            that.bootstrapTable("removeAll");
        };
        this.refreshOptions = function () {
            that.bootstrapTable("refreshOptions");
        };
        this.hidecolumn = function (params) {
            that.bootstrapTable("hideColumn", params);
        };
        this.removeByUniqueId = function (params) {
            that.bootstrapTable("removeByUniqueId", params);
        };
        this.remove = function (params) {
            that.bootstrapTable("remove", params);
        };
        this.hideRow = function (params) {
            that.bootstrapTable("hideRow", params);
        };
        this.showRow = function (params) {
            that.bootstrapTable("showRow", params);
        };
        this.getData = function (params) {
            that.bootstrapTable("getData");
        };
        this.load = function (params) {
            that.bootstrapTable("load", params);
        };
    };
})(jQuery);

$(function () {
    $("#reset").bind('click',function () {
        function clearInputFile(f){
            if(f.value){
                try{
                    f.value = ''; //for IE11, latest Chrome/Firefox/Opera...
                }catch(err){
                }
                if(f.value){ //for IE5 ~ IE10
                    var form = document.createElement('form'), ref = f.nextSibling, p = f.parentNode;
                    form.appendChild(f);
                    form.reset();
                    p.insertBefore(f,ref);
                }
            }
        }
    });
});

$(function (){
    $(".form_datetime").datetimepicker({
        format: "yyyy-mm-dd hh:ii",
        autoclose: true,
        todayBtn: true,
        language:'zh-CN',
        minView: 0,
        maxView: 1,
        todayHighlight: 1,
        pickerPosition:"bottom-right"
    });
});

$(function (){
    $('.selectpicker').selectpicker({
        style: 'btn-default',
        width: "auto",
        size: 10,
        showSubtext:true,
    });
});

toastr.options = {  
        closeButton: false,  
        debug: false,  
        progressBar: true,  
        positionClass: "toast-top-middle",  
        onclick: null,  
        showDuration: "300",  
        hideDuration: "1000",  
        timeOut: "2000",  
        extendedTimeOut: "1000",  
        showEasing: "swing",  
        hideEasing: "linear",  
        showMethod: "fadeIn",  
        hideMethod: "fadeOut"  
    };  