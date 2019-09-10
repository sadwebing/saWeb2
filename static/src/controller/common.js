/**

 @Name：layuiAdmin 公共业务
 @Author：贤心
 @Site：http://www.layui.com/admin/
 @License：LPPL
    
 */
 
layui.define(function(exports){
  var $ = layui.$
  ,layer = layui.layer
  ,laytpl = layui.laytpl
  ,setter = layui.setter
  ,view = layui.view
  ,admin = layui.admin
  
  //公共业务的逻辑处理可以写在此处，切换任何页面都会执行
  //……
  
  
  
  //退出
  admin.events.logout = function(){
    var redirct_to = window.location.hash;

    //执行退出接口
    admin.req({
      url: '/control/logout'
      ,type: 'post'
      ,data:{}
      ,done: function(res){ //这里要说明一下：done 是只有 response 的 code 正常才会执行。而 succese 则是只要 http 为 200 就会执行
        
        //登出的提示
        layer.msg(res.msg, {
          offset: '15px'
          ,icon: 1
          ,time: 1000
        });

        //清空本地记录的 token，并跳转到登入页
        admin.exit();
      },success: function(res){
        if (res.code == 1001){
          layer.msg(res.msg, {
            offset: '15px'
            ,icon: 1
            ,time: 1000
          })
        }
      }
    });
  };

  
  //对外暴露的接口
  exports('common', {});
});