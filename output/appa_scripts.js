
--- SCRIPT ---

var isIe=(document.all)?true:false;
//讓背景漸漸變暗
function showBackground(obj,endInt)
{
	if(isIe)
	{
		obj.filters.alpha.opacity+=20;
		if(obj.filters.alpha.opacity<endInt)
		{
			setTimeout(function(){showBackground(obj,endInt)},5);
		}
	}else{
		var al=parseFloat(obj.style.opacity);al+=0.01;
		obj.style.opacity=al;
		if(al<(endInt/100))
		{setTimeout(function(){showBackground(obj,endInt)},5);}
		}
}

//關閉視窗
function closeWindow()
{
if(document.getElementById('back')!=null)
{
document.getElementById('back').parentNode.removeChild(document.getElementById('back'));
}
if(document.getElementById('mesWindow')!=null)
{
document.getElementById('mesWindow').parentNode.removeChild(document.getElementById('mesWindow'));
}
}

//彈出訊息 START=============================================================================
function PALERT(wTitle,content,pos,wWidth,GoURL,EXT_BUTTON)
{
	closeWindow();
	var bWidth=parseInt(document.documentElement.scrollWidth);
	var bHeight=parseInt(document.documentElement.scrollHeight);
	var back=document.createElement("div");
	back.id="back";
	var styleStr="top:0px;left:0px;position:absolute;background:#666;width:"+bWidth+"px;height:"+bHeight+"px;";
	styleStr+=(isIe)?"filter:alpha(opacity=0);":"opacity:0;";
	back.style.cssText=styleStr;
	document.body.appendChild(back);
	showBackground(back,80);
	var mesW=document.createElement("div");
	mesW.id="mesWindow";
	mesW.className="mesWindow";
	mesW.innerHTML="<div class='mesWindowTop' ><table width='100%' height='100%' style='background:darkblue;'><tr><td style='background:darkblue;' align=center><font color=yellow>"+wTitle+"</font></td><td style='width:1px;background:darkblue;fontcolor:yellow;'><input type='button' name='btt' id='btt' onclick='"+GoURL+"'' title='關閉視窗' class='close' value='關閉' /></td></tr></table></div>";
	mesW.innerHTML=mesW.innerHTML+"<div class='mesWindowContent' id='mesWindowContent' ><center><font color=darkblue size=3>"+content+"</center></div><div class='mesWindowBottom'><center>"+EXT_BUTTON+"</center></div>";
	//跟物件
	//styleStr="left:"+(((pos.x-wWidth)>0)?(pos.x-wWidth):pos.x)+"px;top:"+(pos.y)+"px;position:absolute;width:"+wWidth+"px;";
	//置中
	styleStr="left:"+(bWidth/2-wWidth/2)+"px;top:"+(bHeight/2-100)+"px;position:absolute;width:"+wWidth+"px;";
	mesW.style.cssText=styleStr;
	document.body.appendChild(mesW);
	btt.focus();
}

function P_alert(CONT,TITLE,GoURL,EXT_BUTTON)
{
if(TITLE=='')
{
	TITLE='提示訊息';
}
	messContent="<div style='padding:20px 0 20px 0;text-align:center'>"+CONT+"</div>";
	PALERT(TITLE,messContent,"x:100;y:100",250,GoURL,EXT_BUTTON);
}
//彈出訊息 END=============================================================================

//開新網頁 START==================================================================================
function POPEN(wTitle,content,pos,wWidth)
{
	closeWindow();
	var bWidth=parseInt(document.documentElement.scrollWidth);
	var bHeight=parseInt(document.documentElement.scrollHeight);
	var back=document.createElement("div");
	back.id="back";
	var styleStr="top:0px;left:0px;position:absolute;background:#666;width:"+bWidth+"px;height:"+bHeight+"px;";
	styleStr+=(isIe)?"filter:alpha(opacity=0);":"opacity:0;";
	back.style.cssText=styleStr;
	document.body.appendChild(back);
	showBackground(back,80);
	var mesW=document.createElement("div");
	mesW.id="mesWindow";
	mesW.className="mesWindow";
	mesW.innerHTML="<div class='mesWindowTop' ><table width='100%' height='100%' style='background:darkblue;'><tr><td style='background:darkblue;' align=center><font color=yellow>"+wTitle+"</font></td><td style='width:1px;background:darkblue;fontcolor:yellow;'><input type='button' name='btt' id='btt' onclick='closeWindow();' title='關閉視窗' class='close' value='關閉' /></td></tr></table></div>";
	mesW.innerHTML=mesW.innerHTML+"<div class='mesWindowContent' id='mesWindowContent' ><center><font color=darkblue size=3><iframe name=I1 id=I1 width=700 height=500 src="+content+"></iframe></center></div>";
	//跟物件
	//styleStr="left:"+(((pos.x-wWidth)>0)?(pos.x-wWidth):pos.x)+"px;top:"+(pos.y)+"px;position:absolute;width:"+wWidth+"px;";
	//置中
	styleStr="left:"+(bWidth/2-wWidth/2)+"px;top:0px;position:absolute;width:"+wWidth+"px;";
	mesW.style.cssText=styleStr;
	document.body.appendChild(mesW);
	btt.focus();
}

function P_OPEN(URL,TITLE)
{
if(TITLE=='')
{
	TITLE='網頁';
}
	messContent="<div style='padding:20px 0 20px 0;text-align:center'>"+URL+"</div>";
	POPEN(TITLE,messContent,"x:100;y:100",700);
}

function P_WCLOSE(URL,TITLE)
{
if(TITLE=='')
{
	TITLE='網頁';
}
	messContent="<div style='padding:20px 0 20px 0;text-align:center'>"+URL+"</div>";
	POPEN(TITLE,messContent,"x:100;y:100",700);
}
//開新網頁 END==================================================================================

//開網頁 START============================================================================
function WINCLOSE(wTitle,content,pos,wWidth)
{
	closeWindow();
	var bWidth=parseInt(document.documentElement.scrollWidth);
	var bHeight=parseInt(document.documentElement.scrollHeight);
	var back=document.createElement("div");
	back.id="back";
	var styleStr="top:0px;left:0px;position:absolute;background:#666;width:"+bWidth+"px;height:"+bHeight+"px;";
	styleStr+=(isIe)?"filter:alpha(opacity=0);":"opacity:0;";
	back.style.cssText=styleStr;
	document.body.appendChild(back);
	showBackground(back,80);
	var mesW=document.createElement("div");
	mesW.id="mesWindow";
	mesW.className="mesWindow";
	mesW.innerHTML="<div class='mesWindowTop' ><table width='100%' height='100%' style='background:darkblue;'><tr><td style='background:darkblue;' align=center><font color=yellow>"+wTitle+"</font></td></tr></table></div>";
	mesW.innerHTML=mesW.innerHTML+"<div class='mesWindowContent' id='mesWindowContent' ><center><font color=darkblue size=3>"+content+"</center></div>";
	//跟物件
	//styleStr="left:"+(((pos.x-wWidth)>0)?(pos.x-wWidth):pos.x)+"px;top:"+(pos.y)+"px;position:absolute;width:"+wWidth+"px;";
	//置中
	styleStr="left:"+(bWidth/2-wWidth/2)+"px;top:"+(bHeight/2-100)+"px;position:absolute;width:"+wWidth+"px;";
	mesW.style.cssText=styleStr;
	document.body.appendChild(mesW);
}

function WIN_COLSE(CONT)
{
	TITLE='處理中，請稍候';
	messContent="<div style='padding:20px 0 20px 0;text-align:center'>"+CONT+"</div>";
	WINCLOSE(TITLE,messContent,"x:100;y:100",250);
}

function WIN_OPEN()
{
	closeWindow();
}
//鎖/開網頁 END================================================================================

--- SCRIPT ---

   if(screen.availWidth>1024)
	{
	   document.write("<link rel=stylesheet href=../CSS_Q/1280LSTY.css type=text/css>");
	   document.write("<body background=../APS_IMG_Q/PCG/ACCAPP1280_BOTTOM.gif>");
	 }
	 else
	 {
	   document.write("<link rel=stylesheet href=../CSS_Q/1024LSTY.css type=text/css>");
	   document.write("<body background=../APS_IMG_Q/PCG/ACCAPP_BOTTOM.gif>");	   
	 }

--- SCRIPT ---

function disableInfo() {  
    document.onkeydown = function() {  
        var e = window.event || arguments[0];  
        //F12  
        if(e.keyCode == 123) {  
			alert("禁用F12");
            return false;  
            //Ctrl+Shift+I  
        } else if((e.ctrlKey) && (e.shiftKey) && (e.keyCode == 73)) {  
		    alert("禁用鍵");
            return false;  
            //Shift+F10  
        } else if((e.shiftKey) && (e.keyCode == 121)){  
		    alert("禁用F10");
            return false;  
        }  
    };  
    //右鍵  
    document.oncontextmenu = function() { 
		alert("禁用右鍵"); 
        return false;  
    }  
}

--- SCRIPT ---
    
    function CharToAsc(STR)
    {
        var X_STR = "";
        for(var i =0;i<STR.length;i++){
           X_STR = X_STR +"※"+STR[i].charCodeAt(0).toString();
        }
        X_STR = X_STR.substr(1, X_STR.length - 1)
		return X_STR;
	}

--- SCRIPT ---
    
    function AscToChar(STR)
    {
        Ascs = STR.split("※");
        var A_STR = "";
        for(var i =0;i<Ascs.length;i++){
           A_STR = A_STR+String.fromCharCode(Ascs[i]);
        }
		return A_STR;
	}

--- SCRIPT ---

									
									function CP_1()
									{									   
										if (FORM1.PAYKIND_1.value=="2")
										{
											FORM1.PAYKIND_1.value="1";
											FORM1.PROX_1.checked=false;
										}
										else
										{
											FORM1.PAYKIND_1.value="2";
											FORM1.PROX_1.checked=true;
											
											         alert("代墊者請輸入受款人代號及姓名");
											   
							                                //window.open ("SEAR_VENDORID_SQL_Q.asp?OBNUM=1","查受款人","width=400,height=400,top=1,LEFT=1,toolbar=no,menubar=no,location=no,directories=no,status=no,resizable=1,scrollbars=1");
						                             
						                                    //window.open ("SEAR_VENDORID_Q.asp?OBNUM=1","查受款人","width=400,height=400,top=1,LEFT=1,toolbar=no,menubar=no,location=no,directories=no,status=no,resizable=1,scrollbars=1");
						                             
											CHK_P_1();
										}
									}
								
--- SCRIPT ---

									function QA_1()
									{
										FORM1.INVOICENO_1.value=FORM1.INVOICENO_1.value.toUpperCase();
										if(isNaN(FORM1.INVOICENO_1.value.substr(1,2))==false && FORM1.INVOICENO_1.value!="")
										{
											alert("發票號碼或收據前兩碼必須為文字!!");
											FORM1.INVOICENO_1.value="";
										}
									}
								
--- SCRIPT ---

                								    function CHK_P_1()
                								    {
									
                								        
                                                            //if (FORM1.VENDORID_S_1.value.length!=8 && FORM1.VENDORID_S_1.value.length!=10)
                                                            //{
                                                             //alert("受款人代碼，廠商統編應為8碼、身分證字號10碼，請再檢查是否輸入錯誤！");
                                                             //FORM1.VENDORID_1.value="";
                                                             //FORM1.VENDORID_S_1.value="";
                                                             //return;
                                                            //}
                                                            //if (FORM1.VENDORID_S_1.value.length==8 && isNaN(FORM1.VENDORID_S_1.value))
                                                            //{
                                                             //alert("廠商統編8碼應全為數字、身分證字號則應10碼，請再檢查是否輸入錯誤！");
                                                             //FORM1.VENDORID_1.value="";
                                                             //FORM1.VENDORID_S_1.value="";
                                                             //return;
                                                            //}
                                                      
													  
													     //1081125Karen==>修改時沒重新確定受款人資料，造成代碼與名稱資料不合，故先清空
														 FORM1.VENNAME_1.value="";
														 FORM1.BANKNO_1.value="";
														 FORM1.ACCOUNT_1.value="";
														 FORM1.ACCOUNTNAM_1.value="";
														 FORM1.I_VENDORID_1.value="";
														 
									
                                                    
                                                        if (isNaN(AscToChar(FORM1.VENDORID_1.value).substring(3)))
                								        {
                								            //alert("代碼應為身分證字號或廠商統編，請再檢查是否輸入錯誤！");
                								            //return;
                								            //1030321Karen==>學校常有自編受款人代碼(ex.80225608-1)狀況，故只能提示
                								            alert("受款人代碼應為身分證字號或廠商統編，請再確認是否有誤!!!");
                								        }
                								        if (AscToChar(FORM1.VENDORID_1.value).length==10 && isNaN(AscToChar(FORM1.VENDORID_1.value).substr(1,3))==false && isNaN(AscToChar(FORM1.VENDORID_1.value).substr(0,1))==true)
                								        {
                								            var acc=0;
                								            d0=AscToChar(FORM1.VENDORID_1.value).charAt(0);
                								            d1=AscToChar(FORM1.VENDORID_1.value).charAt(1);
                								            d2=AscToChar(FORM1.VENDORID_1.value).charAt(2);
                								            d3=AscToChar(FORM1.VENDORID_1.value).charAt(3);	
                								            d4=AscToChar(FORM1.VENDORID_1.value).charAt(4);
                								            d5=AscToChar(FORM1.VENDORID_1.value).charAt(5);
                								            d6=AscToChar(FORM1.VENDORID_1.value).charAt(6);
                								            d7=AscToChar(FORM1.VENDORID_1.value).charAt(7);
                								            d8=AscToChar(FORM1.VENDORID_1.value).charAt(8);
                								            d9=AscToChar(FORM1.VENDORID_1.value).charAt(9);
                								            if ((d0=="A")||(d0=="a")){acc=10;}
                								            else if ((d0=="B")||(d0=="b")){acc=11;}
                								            else if ((d0=="C")||(d0=="c")){acc=12;}
                								            else if ((d0=="D")||(d0=="d")){acc=13;}
                								            else if ((d0=="E")||(d0=="e")){acc=14;}
                								            else if ((d0=="F")||(d0=="f")){acc=15;}
                								            else if ((d0=="G")||(d0=="g")){acc=16;}
                								            else if ((d0=="H")||(d0=="h")){acc=17;}
                								            else if ((d0=="J")||(d0=="j")){acc=18;}
                								            else if ((d0=="K")||(d0=="k")){acc=19;}
                								            else if ((d0=="L")||(d0=="l")){acc=20;}
                								            else if ((d0=="M")||(d0=="m")){acc=21;}
                								            else if ((d0=="N")||(d0=="n")){acc=22;}
                								            else if ((d0=="P")||(d0=="p")){acc=23;}
                								            else if ((d0=="Q")||(d0=="q")){acc=24;}
                								            else if ((d0=="R")||(d0=="r")){acc=25;}
                								            else if ((d0=="S")||(d0=="s")){acc=26;}
                								            else if ((d0=="T")||(d0=="t")){acc=27;}
                								            else if ((d0=="U")||(d0=="u")){acc=28;}
                								            else if ((d0=="V")||(d0=="v")){acc=29;}
                								            else if ((d0=="X")||(d0=="x")){acc=30;}
                								            else if ((d0=="Y")||(d0=="y")){acc=31;}
                								            else if ((d0=="W")||(d0=="w")){acc=32;}
                								            else if ((d0=="Z")||(d0=="z")){acc=33;}									   
                								            else if ((d0=="I")||(d0=="i")){acc=34;}
                								            else if ((d0=="O")||(d0=="o")){acc=35;}
                								            if (acc==0)
                								            {
                								                alert("請輸入『身份證號碼』的第一個英文字母！");
                								                FORM1.VENDORID_1.value="";
                								                FORM1.VENDORID_S_1.value="";
                								                return;
                								            }
                								            else
                								            {
                								                accstr = new String(acc);
                								                acc_1 = (accstr).charAt(0);
                								                acc_2 = (accstr).charAt(1);
                								                certsum = 1*acc_1 + 9*acc_2 + 8*d1 + 7*d2 + 6*d3 + 5*d4 + 4*d5 + 3*d6 + 2*d7 + 1*d8;
                								                certsum_2 = parseInt(certsum%10);
                								                if (certsum_2==0){certsum_3 = 0;}
                								                else{certsum_3 = 10 - certsum_2;}                                            
                								                //alert(certsum_3);
                								                if (d9!=certsum_3)
                								                {
                								                    alert("與檢驗碼不符，請再檢查『身份證號碼』是否輸入錯誤！");
                								                    FORM1.VENDORID_1.value="";
                								                    FORM1.VENDORID_S_1.value="";
                								                    return;
                								                }
                								            }									   
                								        }
                								    
                                                        if (!FORM1.VENDORID_1.value=="")
                								        {
                								            parent.parent.CK_VN.FORM1.VENDORID.value=AscToChar(FORM1.VENDORID_1.value).toUpperCase();
                								            parent.parent.CK_VN.FORM1.RE_HAND.value="parent.MAIN.APPA.FORM1";
                								            parent.parent.CK_VN.FORM1.I_J.value="_1";
															parent.parent.CK_VN.FORM1.PAYKIND.value=FORM1.PAYKIND_1.value.toUpperCase();
                								            parent.parent.CK_VN.FORM1.submit();
                								            //STAR_ID_1();
                								        }
                								        //else{
                								        //    if (國立勤益科技大學="宜蘭大學")
                								        //    {
                								        //        if(FORM1.BANKNO_1.value=="" || FORM1.ACCOUNT_1.value==""){
                								        //            parent.par
--- SCRIPT ---

									
									function CP_2()
									{									   
										if (FORM1.PAYKIND_2.value=="2")
										{
											FORM1.PAYKIND_2.value="1";
											FORM1.PROX_2.checked=false;
										}
										else
										{
											FORM1.PAYKIND_2.value="2";
											FORM1.PROX_2.checked=true;
											
											         alert("代墊者請輸入受款人代號及姓名");
											   
							                                //window.open ("SEAR_VENDORID_SQL_Q.asp?OBNUM=2","查受款人","width=400,height=400,top=1,LEFT=1,toolbar=no,menubar=no,location=no,directories=no,status=no,resizable=1,scrollbars=1");
						                             
						                                    //window.open ("SEAR_VENDORID_Q.asp?OBNUM=2","查受款人","width=400,height=400,top=1,LEFT=1,toolbar=no,menubar=no,location=no,directories=no,status=no,resizable=1,scrollbars=1");
						                             
											CHK_P_2();
										}
									}
								
--- SCRIPT ---

									function QA_2()
									{
										FORM1.INVOICENO_2.value=FORM1.INVOICENO_2.value.toUpperCase();
										if(isNaN(FORM1.INVOICENO_2.value.substr(1,2))==false && FORM1.INVOICENO_2.value!="")
										{
											alert("發票號碼或收據前兩碼必須為文字!!");
											FORM1.INVOICENO_2.value="";
										}
									}
								
--- SCRIPT ---

                								    function CHK_P_2()
                								    {
									
                								        
                                                            //if (FORM1.VENDORID_S_2.value.length!=8 && FORM1.VENDORID_S_2.value.length!=10)
                                                            //{
                                                             //alert("受款人代碼，廠商統編應為8碼、身分證字號10碼，請再檢查是否輸入錯誤！");
                                                             //FORM1.VENDORID_2.value="";
                                                             //FORM1.VENDORID_S_2.value="";
                                                             //return;
                                                            //}
                                                            //if (FORM1.VENDORID_S_2.value.length==8 && isNaN(FORM1.VENDORID_S_2.value))
                                                            //{
                                                             //alert("廠商統編8碼應全為數字、身分證字號則應10碼，請再檢查是否輸入錯誤！");
                                                             //FORM1.VENDORID_2.value="";
                                                             //FORM1.VENDORID_S_2.value="";
                                                             //return;
                                                            //}
                                                      
													  
													     //1081125Karen==>修改時沒重新確定受款人資料，造成代碼與名稱資料不合，故先清空
														 FORM1.VENNAME_2.value="";
														 FORM1.BANKNO_2.value="";
														 FORM1.ACCOUNT_2.value="";
														 FORM1.ACCOUNTNAM_2.value="";
														 FORM1.I_VENDORID_2.value="";
														 
									
                                                    
                                                        if (isNaN(AscToChar(FORM1.VENDORID_2.value).substring(3)))
                								        {
                								            //alert("代碼應為身分證字號或廠商統編，請再檢查是否輸入錯誤！");
                								            //return;
                								            //1030321Karen==>學校常有自編受款人代碼(ex.80225608-1)狀況，故只能提示
                								            alert("受款人代碼應為身分證字號或廠商統編，請再確認是否有誤!!!");
                								        }
                								        if (AscToChar(FORM1.VENDORID_2.value).length==10 && isNaN(AscToChar(FORM1.VENDORID_2.value).substr(1,3))==false && isNaN(AscToChar(FORM1.VENDORID_2.value).substr(0,1))==true)
                								        {
                								            var acc=0;
                								            d0=AscToChar(FORM1.VENDORID_2.value).charAt(0);
                								            d1=AscToChar(FORM1.VENDORID_2.value).charAt(1);
                								            d2=AscToChar(FORM1.VENDORID_2.value).charAt(2);
                								            d3=AscToChar(FORM1.VENDORID_2.value).charAt(3);	
                								            d4=AscToChar(FORM1.VENDORID_2.value).charAt(4);
                								            d5=AscToChar(FORM1.VENDORID_2.value).charAt(5);
                								            d6=AscToChar(FORM1.VENDORID_2.value).charAt(6);
                								            d7=AscToChar(FORM1.VENDORID_2.value).charAt(7);
                								            d8=AscToChar(FORM1.VENDORID_2.value).charAt(8);
                								            d9=AscToChar(FORM1.VENDORID_2.value).charAt(9);
                								            if ((d0=="A")||(d0=="a")){acc=10;}
                								            else if ((d0=="B")||(d0=="b")){acc=11;}
                								            else if ((d0=="C")||(d0=="c")){acc=12;}
                								            else if ((d0=="D")||(d0=="d")){acc=13;}
                								            else if ((d0=="E")||(d0=="e")){acc=14;}
                								            else if ((d0=="F")||(d0=="f")){acc=15;}
                								            else if ((d0=="G")||(d0=="g")){acc=16;}
                								            else if ((d0=="H")||(d0=="h")){acc=17;}
                								            else if ((d0=="J")||(d0=="j")){acc=18;}
                								            else if ((d0=="K")||(d0=="k")){acc=19;}
                								            else if ((d0=="L")||(d0=="l")){acc=20;}
                								            else if ((d0=="M")||(d0=="m")){acc=21;}
                								            else if ((d0=="N")||(d0=="n")){acc=22;}
                								            else if ((d0=="P")||(d0=="p")){acc=23;}
                								            else if ((d0=="Q")||(d0=="q")){acc=24;}
                								            else if ((d0=="R")||(d0=="r")){acc=25;}
                								            else if ((d0=="S")||(d0=="s")){acc=26;}
                								            else if ((d0=="T")||(d0=="t")){acc=27;}
                								            else if ((d0=="U")||(d0=="u")){acc=28;}
                								            else if ((d0=="V")||(d0=="v")){acc=29;}
                								            else if ((d0=="X")||(d0=="x")){acc=30;}
                								            else if ((d0=="Y")||(d0=="y")){acc=31;}
                								            else if ((d0=="W")||(d0=="w")){acc=32;}
                								            else if ((d0=="Z")||(d0=="z")){acc=33;}									   
                								            else if ((d0=="I")||(d0=="i")){acc=34;}
                								            else if ((d0=="O")||(d0=="o")){acc=35;}
                								            if (acc==0)
                								            {
                								                alert("請輸入『身份證號碼』的第一個英文字母！");
                								                FORM1.VENDORID_2.value="";
                								                FORM1.VENDORID_S_2.value="";
                								                return;
                								            }
                								            else
                								            {
                								                accstr = new String(acc);
                								                acc_1 = (accstr).charAt(0);
                								                acc_2 = (accstr).charAt(1);
                								                certsum = 1*acc_1 + 9*acc_2 + 8*d1 + 7*d2 + 6*d3 + 5*d4 + 4*d5 + 3*d6 + 2*d7 + 1*d8;
                								                certsum_2 = parseInt(certsum%10);
                								                if (certsum_2==0){certsum_3 = 0;}
                								                else{certsum_3 = 10 - certsum_2;}                                            
                								                //alert(certsum_3);
                								                if (d9!=certsum_3)
                								                {
                								                    alert("與檢驗碼不符，請再檢查『身份證號碼』是否輸入錯誤！");
                								                    FORM1.VENDORID_2.value="";
                								                    FORM1.VENDORID_S_2.value="";
                								                    return;
                								                }
                								            }									   
                								        }
                								    
                                                        if (!FORM1.VENDORID_2.value=="")
                								        {
                								            parent.parent.CK_VN.FORM1.VENDORID.value=AscToChar(FORM1.VENDORID_2.value).toUpperCase();
                								            parent.parent.CK_VN.FORM1.RE_HAND.value="parent.MAIN.APPA.FORM1";
                								            parent.parent.CK_VN.FORM1.I_J.value="_2";
															parent.parent.CK_VN.FORM1.PAYKIND.value=FORM1.PAYKIND_2.value.toUpperCase();
                								            parent.parent.CK_VN.FORM1.submit();
                								            //STAR_ID_2();
                								        }
                								        //else{
                								        //    if (國立勤益科技大學="宜蘭大學")
                								        //    {
                								        //        if(FORM1.BANKNO_2.value=="" || FORM1.ACCOUNT_2.value==""){
                								        //            parent.par
--- SCRIPT ---

									
									function CP_3()
									{									   
										if (FORM1.PAYKIND_3.value=="2")
										{
											FORM1.PAYKIND_3.value="1";
											FORM1.PROX_3.checked=false;
										}
										else
										{
											FORM1.PAYKIND_3.value="2";
											FORM1.PROX_3.checked=true;
											
											         alert("代墊者請輸入受款人代號及姓名");
											   
							                                //window.open ("SEAR_VENDORID_SQL_Q.asp?OBNUM=3","查受款人","width=400,height=400,top=1,LEFT=1,toolbar=no,menubar=no,location=no,directories=no,status=no,resizable=1,scrollbars=1");
						                             
						                                    //window.open ("SEAR_VENDORID_Q.asp?OBNUM=3","查受款人","width=400,height=400,top=1,LEFT=1,toolbar=no,menubar=no,location=no,directories=no,status=no,resizable=1,scrollbars=1");
						                             
											CHK_P_3();
										}
									}
								
--- SCRIPT ---

									function QA_3()
									{
										FORM1.INVOICENO_3.value=FORM1.INVOICENO_3.value.toUpperCase();
										if(isNaN(FORM1.INVOICENO_3.value.substr(1,2))==false && FORM1.INVOICENO_3.value!="")
										{
											alert("發票號碼或收據前兩碼必須為文字!!");
											FORM1.INVOICENO_3.value="";
										}
									}
								
--- SCRIPT ---

                								    function CHK_P_3()
                								    {
									
                								        
                                                            //if (FORM1.VENDORID_S_3.value.length!=8 && FORM1.VENDORID_S_3.value.length!=10)
                                                            //{
                                                             //alert("受款人代碼，廠商統編應為8碼、身分證字號10碼，請再檢查是否輸入錯誤！");
                                                             //FORM1.VENDORID_3.value="";
                                                             //FORM1.VENDORID_S_3.value="";
                                                             //return;
                                                            //}
                                                            //if (FORM1.VENDORID_S_3.value.length==8 && isNaN(FORM1.VENDORID_S_3.value))
                                                            //{
                                                             //alert("廠商統編8碼應全為數字、身分證字號則應10碼，請再檢查是否輸入錯誤！");
                                                             //FORM1.VENDORID_3.value="";
                                                             //FORM1.VENDORID_S_3.value="";
                                                             //return;
                                                            //}
                                                      
													  
													     //1081125Karen==>修改時沒重新確定受款人資料，造成代碼與名稱資料不合，故先清空
														 FORM1.VENNAME_3.value="";
														 FORM1.BANKNO_3.value="";
														 FORM1.ACCOUNT_3.value="";
														 FORM1.ACCOUNTNAM_3.value="";
														 FORM1.I_VENDORID_3.value="";
														 
									
                                                    
                                                        if (isNaN(AscToChar(FORM1.VENDORID_3.value).substring(3)))
                								        {
                								            //alert("代碼應為身分證字號或廠商統編，請再檢查是否輸入錯誤！");
                								            //return;
                								            //1030321Karen==>學校常有自編受款人代碼(ex.80225608-1)狀況，故只能提示
                								            alert("受款人代碼應為身分證字號或廠商統編，請再確認是否有誤!!!");
                								        }
                								        if (AscToChar(FORM1.VENDORID_3.value).length==10 && isNaN(AscToChar(FORM1.VENDORID_3.value).substr(1,3))==false && isNaN(AscToChar(FORM1.VENDORID_3.value).substr(0,1))==true)
                								        {
                								            var acc=0;
                								            d0=AscToChar(FORM1.VENDORID_3.value).charAt(0);
                								            d1=AscToChar(FORM1.VENDORID_3.value).charAt(1);
                								            d2=AscToChar(FORM1.VENDORID_3.value).charAt(2);
                								            d3=AscToChar(FORM1.VENDORID_3.value).charAt(3);	
                								            d4=AscToChar(FORM1.VENDORID_3.value).charAt(4);
                								            d5=AscToChar(FORM1.VENDORID_3.value).charAt(5);
                								            d6=AscToChar(FORM1.VENDORID_3.value).charAt(6);
                								            d7=AscToChar(FORM1.VENDORID_3.value).charAt(7);
                								            d8=AscToChar(FORM1.VENDORID_3.value).charAt(8);
                								            d9=AscToChar(FORM1.VENDORID_3.value).charAt(9);
                								            if ((d0=="A")||(d0=="a")){acc=10;}
                								            else if ((d0=="B")||(d0=="b")){acc=11;}
                								            else if ((d0=="C")||(d0=="c")){acc=12;}
                								            else if ((d0=="D")||(d0=="d")){acc=13;}
                								            else if ((d0=="E")||(d0=="e")){acc=14;}
                								            else if ((d0=="F")||(d0=="f")){acc=15;}
                								            else if ((d0=="G")||(d0=="g")){acc=16;}
                								            else if ((d0=="H")||(d0=="h")){acc=17;}
                								            else if ((d0=="J")||(d0=="j")){acc=18;}
                								            else if ((d0=="K")||(d0=="k")){acc=19;}
                								            else if ((d0=="L")||(d0=="l")){acc=20;}
                								            else if ((d0=="M")||(d0=="m")){acc=21;}
                								            else if ((d0=="N")||(d0=="n")){acc=22;}
                								            else if ((d0=="P")||(d0=="p")){acc=23;}
                								            else if ((d0=="Q")||(d0=="q")){acc=24;}
                								            else if ((d0=="R")||(d0=="r")){acc=25;}
                								            else if ((d0=="S")||(d0=="s")){acc=26;}
                								            else if ((d0=="T")||(d0=="t")){acc=27;}
                								            else if ((d0=="U")||(d0=="u")){acc=28;}
                								            else if ((d0=="V")||(d0=="v")){acc=29;}
                								            else if ((d0=="X")||(d0=="x")){acc=30;}
                								            else if ((d0=="Y")||(d0=="y")){acc=31;}
                								            else if ((d0=="W")||(d0=="w")){acc=32;}
                								            else if ((d0=="Z")||(d0=="z")){acc=33;}									   
                								            else if ((d0=="I")||(d0=="i")){acc=34;}
                								            else if ((d0=="O")||(d0=="o")){acc=35;}
                								            if (acc==0)
                								            {
                								                alert("請輸入『身份證號碼』的第一個英文字母！");
                								                FORM1.VENDORID_3.value="";
                								                FORM1.VENDORID_S_3.value="";
                								                return;
                								            }
                								            else
                								            {
                								                accstr = new String(acc);
                								                acc_1 = (accstr).charAt(0);
                								                acc_2 = (accstr).charAt(1);
                								                certsum = 1*acc_1 + 9*acc_2 + 8*d1 + 7*d2 + 6*d3 + 5*d4 + 4*d5 + 3*d6 + 2*d7 + 1*d8;
                								                certsum_2 = parseInt(certsum%10);
                								                if (certsum_2==0){certsum_3 = 0;}
                								                else{certsum_3 = 10 - certsum_2;}                                            
                								                //alert(certsum_3);
                								                if (d9!=certsum_3)
                								                {
                								                    alert("與檢驗碼不符，請再檢查『身份證號碼』是否輸入錯誤！");
                								                    FORM1.VENDORID_3.value="";
                								                    FORM1.VENDORID_S_3.value="";
                								                    return;
                								                }
                								            }									   
                								        }
                								    
                                                        if (!FORM1.VENDORID_3.value=="")
                								        {
                								            parent.parent.CK_VN.FORM1.VENDORID.value=AscToChar(FORM1.VENDORID_3.value).toUpperCase();
                								            parent.parent.CK_VN.FORM1.RE_HAND.value="parent.MAIN.APPA.FORM1";
                								            parent.parent.CK_VN.FORM1.I_J.value="_3";
															parent.parent.CK_VN.FORM1.PAYKIND.value=FORM1.PAYKIND_3.value.toUpperCase();
                								            parent.parent.CK_VN.FORM1.submit();
                								            //STAR_ID_3();
                								        }
                								        //else{
                								        //    if (國立勤益科技大學="宜蘭大學")
                								        //    {
                								        //        if(FORM1.BANKNO_3.value=="" || FORM1.ACCOUNT_3.value==""){
                								        //            parent.par
--- SCRIPT ---

									
									function CP_4()
									{									   
										if (FORM1.PAYKIND_4.value=="2")
										{
											FORM1.PAYKIND_4.value="1";
											FORM1.PROX_4.checked=false;
										}
										else
										{
											FORM1.PAYKIND_4.value="2";
											FORM1.PROX_4.checked=true;
											
											         alert("代墊者請輸入受款人代號及姓名");
											   
							                                //window.open ("SEAR_VENDORID_SQL_Q.asp?OBNUM=4","查受款人","width=400,height=400,top=1,LEFT=1,toolbar=no,menubar=no,location=no,directories=no,status=no,resizable=1,scrollbars=1");
						                             
						                                    //window.open ("SEAR_VENDORID_Q.asp?OBNUM=4","查受款人","width=400,height=400,top=1,LEFT=1,toolbar=no,menubar=no,location=no,directories=no,status=no,resizable=1,scrollbars=1");
						                             
											CHK_P_4();
										}
									}
								
--- SCRIPT ---

									function QA_4()
									{
										FORM1.INVOICENO_4.value=FORM1.INVOICENO_4.value.toUpperCase();
										if(isNaN(FORM1.INVOICENO_4.value.substr(1,2))==false && FORM1.INVOICENO_4.value!="")
										{
											alert("發票號碼或收據前兩碼必須為文字!!");
											FORM1.INVOICENO_4.value="";
										}
									}
								
--- SCRIPT ---

                								    function CHK_P_4()
                								    {
									
                								        
                                                            //if (FORM1.VENDORID_S_4.value.length!=8 && FORM1.VENDORID_S_4.value.length!=10)
                                                            //{
                                                             //alert("受款人代碼，廠商統編應為8碼、身分證字號10碼，請再檢查是否輸入錯誤！");
                                                             //FORM1.VENDORID_4.value="";
                                                             //FORM1.VENDORID_S_4.value="";
                                                             //return;
                                                            //}
                                                            //if (FORM1.VENDORID_S_4.value.length==8 && isNaN(FORM1.VENDORID_S_4.value))
                                                            //{
                                                             //alert("廠商統編8碼應全為數字、身分證字號則應10碼，請再檢查是否輸入錯誤！");
                                                             //FORM1.VENDORID_4.value="";
                                                             //FORM1.VENDORID_S_4.value="";
                                                             //return;
                                                            //}
                                                      
													  
													     //1081125Karen==>修改時沒重新確定受款人資料，造成代碼與名稱資料不合，故先清空
														 FORM1.VENNAME_4.value="";
														 FORM1.BANKNO_4.value="";
														 FORM1.ACCOUNT_4.value="";
														 FORM1.ACCOUNTNAM_4.value="";
														 FORM1.I_VENDORID_4.value="";
														 
									
                                                    
                                                        if (isNaN(AscToChar(FORM1.VENDORID_4.value).substring(3)))
                								        {
                								            //alert("代碼應為身分證字號或廠商統編，請再檢查是否輸入錯誤！");
                								            //return;
                								            //1030321Karen==>學校常有自編受款人代碼(ex.80225608-1)狀況，故只能提示
                								            alert("受款人代碼應為身分證字號或廠商統編，請再確認是否有誤!!!");
                								        }
                								        if (AscToChar(FORM1.VENDORID_4.value).length==10 && isNaN(AscToChar(FORM1.VENDORID_4.value).substr(1,3))==false && isNaN(AscToChar(FORM1.VENDORID_4.value).substr(0,1))==true)
                								        {
                								            var acc=0;
                								            d0=AscToChar(FORM1.VENDORID_4.value).charAt(0);
                								            d1=AscToChar(FORM1.VENDORID_4.value).charAt(1);
                								            d2=AscToChar(FORM1.VENDORID_4.value).charAt(2);
                								            d3=AscToChar(FORM1.VENDORID_4.value).charAt(3);	
                								            d4=AscToChar(FORM1.VENDORID_4.value).charAt(4);
                								            d5=AscToChar(FORM1.VENDORID_4.value).charAt(5);
                								            d6=AscToChar(FORM1.VENDORID_4.value).charAt(6);
                								            d7=AscToChar(FORM1.VENDORID_4.value).charAt(7);
                								            d8=AscToChar(FORM1.VENDORID_4.value).charAt(8);
                								            d9=AscToChar(FORM1.VENDORID_4.value).charAt(9);
                								            if ((d0=="A")||(d0=="a")){acc=10;}
                								            else if ((d0=="B")||(d0=="b")){acc=11;}
                								            else if ((d0=="C")||(d0=="c")){acc=12;}
                								            else if ((d0=="D")||(d0=="d")){acc=13;}
                								            else if ((d0=="E")||(d0=="e")){acc=14;}
                								            else if ((d0=="F")||(d0=="f")){acc=15;}
                								            else if ((d0=="G")||(d0=="g")){acc=16;}
                								            else if ((d0=="H")||(d0=="h")){acc=17;}
                								            else if ((d0=="J")||(d0=="j")){acc=18;}
                								            else if ((d0=="K")||(d0=="k")){acc=19;}
                								            else if ((d0=="L")||(d0=="l")){acc=20;}
                								            else if ((d0=="M")||(d0=="m")){acc=21;}
                								            else if ((d0=="N")||(d0=="n")){acc=22;}
                								            else if ((d0=="P")||(d0=="p")){acc=23;}
                								            else if ((d0=="Q")||(d0=="q")){acc=24;}
                								            else if ((d0=="R")||(d0=="r")){acc=25;}
                								            else if ((d0=="S")||(d0=="s")){acc=26;}
                								            else if ((d0=="T")||(d0=="t")){acc=27;}
                								            else if ((d0=="U")||(d0=="u")){acc=28;}
                								            else if ((d0=="V")||(d0=="v")){acc=29;}
                								            else if ((d0=="X")||(d0=="x")){acc=30;}
                								            else if ((d0=="Y")||(d0=="y")){acc=31;}
                								            else if ((d0=="W")||(d0=="w")){acc=32;}
                								            else if ((d0=="Z")||(d0=="z")){acc=33;}									   
                								            else if ((d0=="I")||(d0=="i")){acc=34;}
                								            else if ((d0=="O")||(d0=="o")){acc=35;}
                								            if (acc==0)
                								            {
                								                alert("請輸入『身份證號碼』的第一個英文字母！");
                								                FORM1.VENDORID_4.value="";
                								                FORM1.VENDORID_S_4.value="";
                								                return;
                								            }
                								            else
                								            {
                								                accstr = new String(acc);
                								                acc_1 = (accstr).charAt(0);
                								                acc_2 = (accstr).charAt(1);
                								                certsum = 1*acc_1 + 9*acc_2 + 8*d1 + 7*d2 + 6*d3 + 5*d4 + 4*d5 + 3*d6 + 2*d7 + 1*d8;
                								                certsum_2 = parseInt(certsum%10);
                								                if (certsum_2==0){certsum_3 = 0;}
                								                else{certsum_3 = 10 - certsum_2;}                                            
                								                //alert(certsum_3);
                								                if (d9!=certsum_3)
                								                {
                								                    alert("與檢驗碼不符，請再檢查『身份證號碼』是否輸入錯誤！");
                								                    FORM1.VENDORID_4.value="";
                								                    FORM1.VENDORID_S_4.value="";
                								                    return;
                								                }
                								            }									   
                								        }
                								    
                                                        if (!FORM1.VENDORID_4.value=="")
                								        {
                								            parent.parent.CK_VN.FORM1.VENDORID.value=AscToChar(FORM1.VENDORID_4.value).toUpperCase();
                								            parent.parent.CK_VN.FORM1.RE_HAND.value="parent.MAIN.APPA.FORM1";
                								            parent.parent.CK_VN.FORM1.I_J.value="_4";
															parent.parent.CK_VN.FORM1.PAYKIND.value=FORM1.PAYKIND_4.value.toUpperCase();
                								            parent.parent.CK_VN.FORM1.submit();
                								            //STAR_ID_4();
                								        }
                								        //else{
                								        //    if (國立勤益科技大學="宜蘭大學")
                								        //    {
                								        //        if(FORM1.BANKNO_4.value=="" || FORM1.ACCOUNT_4.value==""){
                								        //            parent.par
--- SCRIPT ---

									
									function CP_5()
									{									   
										if (FORM1.PAYKIND_5.value=="2")
										{
											FORM1.PAYKIND_5.value="1";
											FORM1.PROX_5.checked=false;
										}
										else
										{
											FORM1.PAYKIND_5.value="2";
											FORM1.PROX_5.checked=true;
											
											         alert("代墊者請輸入受款人代號及姓名");
											   
							                                //window.open ("SEAR_VENDORID_SQL_Q.asp?OBNUM=5","查受款人","width=400,height=400,top=1,LEFT=1,toolbar=no,menubar=no,location=no,directories=no,status=no,resizable=1,scrollbars=1");
						                             
						                                    //window.open ("SEAR_VENDORID_Q.asp?OBNUM=5","查受款人","width=400,height=400,top=1,LEFT=1,toolbar=no,menubar=no,location=no,directories=no,status=no,resizable=1,scrollbars=1");
						                             
											CHK_P_5();
										}
									}
								
--- SCRIPT ---

									function QA_5()
									{
										FORM1.INVOICENO_5.value=FORM1.INVOICENO_5.value.toUpperCase();
										if(isNaN(FORM1.INVOICENO_5.value.substr(1,2))==false && FORM1.INVOICENO_5.value!="")
										{
											alert("發票號碼或收據前兩碼必須為文字!!");
											FORM1.INVOICENO_5.value="";
										}
									}
								
--- SCRIPT ---

                								    function CHK_P_5()
                								    {
									
                								        
                                                            //if (FORM1.VENDORID_S_5.value.length!=8 && FORM1.VENDORID_S_5.value.length!=10)
                                                            //{
                                                             //alert("受款人代碼，廠商統編應為8碼、身分證字號10碼，請再檢查是否輸入錯誤！");
                                                             //FORM1.VENDORID_5.value="";
                                                             //FORM1.VENDORID_S_5.value="";
                                                             //return;
                                                            //}
                                                            //if (FORM1.VENDORID_S_5.value.length==8 && isNaN(FORM1.VENDORID_S_5.value))
                                                            //{
                                                             //alert("廠商統編8碼應全為數字、身分證字號則應10碼，請再檢查是否輸入錯誤！");
                                                             //FORM1.VENDORID_5.value="";
                                                             //FORM1.VENDORID_S_5.value="";
                                                             //return;
                                                            //}
                                                      
													  
													     //1081125Karen==>修改時沒重新確定受款人資料，造成代碼與名稱資料不合，故先清空
														 FORM1.VENNAME_5.value="";
														 FORM1.BANKNO_5.value="";
														 FORM1.ACCOUNT_5.value="";
														 FORM1.ACCOUNTNAM_5.value="";
														 FORM1.I_VENDORID_5.value="";
														 
									
                                                    
                                                        if (isNaN(AscToChar(FORM1.VENDORID_5.value).substring(3)))
                								        {
                								            //alert("代碼應為身分證字號或廠商統編，請再檢查是否輸入錯誤！");
                								            //return;
                								            //1030321Karen==>學校常有自編受款人代碼(ex.80225608-1)狀況，故只能提示
                								            alert("受款人代碼應為身分證字號或廠商統編，請再確認是否有誤!!!");
                								        }
                								        if (AscToChar(FORM1.VENDORID_5.value).length==10 && isNaN(AscToChar(FORM1.VENDORID_5.value).substr(1,3))==false && isNaN(AscToChar(FORM1.VENDORID_5.value).substr(0,1))==true)
                								        {
                								            var acc=0;
                								            d0=AscToChar(FORM1.VENDORID_5.value).charAt(0);
                								            d1=AscToChar(FORM1.VENDORID_5.value).charAt(1);
                								            d2=AscToChar(FORM1.VENDORID_5.value).charAt(2);
                								            d3=AscToChar(FORM1.VENDORID_5.value).charAt(3);	
                								            d4=AscToChar(FORM1.VENDORID_5.value).charAt(4);
                								            d5=AscToChar(FORM1.VENDORID_5.value).charAt(5);
                								            d6=AscToChar(FORM1.VENDORID_5.value).charAt(6);
                								            d7=AscToChar(FORM1.VENDORID_5.value).charAt(7);
                								            d8=AscToChar(FORM1.VENDORID_5.value).charAt(8);
                								            d9=AscToChar(FORM1.VENDORID_5.value).charAt(9);
                								            if ((d0=="A")||(d0=="a")){acc=10;}
                					