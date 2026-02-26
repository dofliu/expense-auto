
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
	var bHeight=parseInt(document.documentElement.scrol
--- SCRIPT ---

   if(screen.availWidth>1024)
	{
	   document.write("<link rel=stylesheet href=../CSS_Q/1280LSTY.css type=text/css>");
	   document.write("<body background=../APS_IMG_Q/PCG/AccSQLWEB1280_BOTTOM.gif>"); 
	 }
	 else
	 {
	   document.write("<link rel=stylesheet href=../CSS_Q/1024LSTY.css type=text/css>");
	   document.write("<body background=../APS_IMG_Q/PCG/AccSQLWEB1024_BOTTOM.gif>");	   
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
        Chars = STR.split("※");
        var X_STR = "";
        for(var i =0;i<chars.length;i++){
           X_STR = X_STR +"※"+chars[i].charCodeAt(0).toString();
        }
        X_STR.substr(1,X_STR.length-1)
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

                    function ACPPYO(){
                        if( parent.APPP.FORM1.PRODUCT_1.value==""){							
							parent.APPP.FORM1.PRODUCT_1.value="詳如附件"
                        }
                        var ISVOUCHK="True";
                        if(ISVOUCHK=="True"){
                            if( parent.APPA.FORM1.INVOICENO_1.value==""){
                                parent.APPA.FORM1.INVOICENO_1.value="詳如清冊"
								parent.APPA.FORM1.VENDORID_1.value="XX01";
                                parent.APPA.FORM1.VENDORID_S_1.value="XX001"
                                parent.APPA.FORM1.VENNAME_1.value="詳如清冊"
                            }
                        }
                    }

                
--- SCRIPT ---

					 
					    FORM1.ISPERI.value="N";			 			
					 
					 
--- SCRIPT ---

			    function CHK_APPP()
				{
				  parent.APPP.FORM1.SUM_LIST.click();
				  FORM1.SUM_APPP.value=parent.APPP.FORM1.SUM_LIST.value;
				}
			
--- SCRIPT ---

			    function CHK_APPA()
				{
				  parent.APPA.FORM1.SUM_LIST.click();
				  FORM1.SUM_APPA.value=parent.APPA.SUM_LIST.value;
				}
			
--- SCRIPT ---

	function  CHK_VOUSERNO()
	{
		FORM1.VOU_SERNO.value=FORM1.VOU_SERNO.value.toUpperCase();
		if (FORM1.VOU_SERNO.value==FORM1.APYUSERNO.value)
		{
		  alert("報銷人不可指定自己!!");
		  FORM1.VOU_SERNO.value="";
		}
		
		if (!FORM1.VOU_SERNO.value=="")
		{
		  window.open("SEAR_VOUSERNO_Q.asp?ID="+FORM1.VOU_SERNO.value+"","","width=20,height=50,top=1,LEFT=1,toolbar=no,menubar=no,location=no,directories=no,status=no,resizable=1,scrollbars=1");
		}
	}
	
--- SCRIPT ---

			    			FORM1.F1.click();
		   				 
--- SCRIPT ---

									//抓回CO之BUGET元素中之值(BUGETNO#BUGNAME@BUGETNO#BUGNAME)
									
										CO_BUGET_VA=parent.parent.TRAN.FORM2.BUGET.value;
						  			
						  			//切Array
									A_CO_BUGET_VA=CO_BUGET_VA.split("@");
									//算Array長度
									N_CO_BUGET_VA=A_CO_BUGET_VA.length;
									//alert(N_CO_BUGET_VA);
									
									//定義select之option之數量
									var BUGETS_STR;
									
										BUGETS_STR=parent.parent.TRAN.FORM2.BUGETS.value;//+FORM1.APPY_BUGETS.value;
									
									T_A_BS=new Array();
									T_A_BS=BUGETS_STR.split("@");
									T_N_BS=T_A_BS.length;
									//alert(BUGETS_STR);
									
									//抓回SUBJECTNO元素之值
						  			T_A_SJ=new Array();
						 			T_A_SJ=parent.parent.TRAN.FORM2.SUBJECTNO.value.split("@");
						  			T_N_SJ=T_A_SJ.length;
									
									//抓回APYKIND之值
									T_A_AK=new Array();
						 			T_A_AK=parent.parent.TRAN.FORM2.APYKIND.value.split("@");
						  			T_N_AK=T_A_AK.length;
								
--- SCRIPT ---

										FORM1.BUGETNO_1.length=N_CO_BUGET_VA;
										//跑回圈加入到SELECT中
										FORM1.BUGETNO_1.options[0].value="";
										FORM1.BUGETNO_1.options[0].text="請先【點選本格】下拉選擇經費";
										FORM1.BUGETNO_1.options[0].style.color="red";
										for(TB=0;TB<N_CO_BUGET_VA-1;TB++)
										{
											FORM1.BUGETNO_1.options[TB+1].value=A_CO_BUGET_VA[TB].split("#")[0];
											FORM1.BUGETNO_1.options[TB+1].text="【"+A_CO_BUGET_VA[TB].split("#")[0]+"】"+A_CO_BUGET_VA[TB].split("#")[1];
										}
											
									
--- SCRIPT ---

								
								//建立一個
								function BN_1()
								{
									var TQS_1="##下拉選擇經費用途#@";
									//將BUGETNO.VALUE送到HI
									for(TQ=0;TQ<T_N_BS-1;TQ++)
									{
										//組出可用之bugets之字串
										T_A_BS_A=T_A_BS[TQ].split("#");
										if(T_A_BS_A[0]==FORM1.BUGETNO_1.value)
										{
											TQS_1=TQS_1+T_A_BS[TQ]+"@";
										}
									}
									//再把字串切Array放到BUGCODE_?中
									A_BGC=new Array();
									A_BGC=TQS_1.split("@");
									N_BGC=A_BGC.length;
									//設定BUGCODE_之option數
									FORM1.BUGCODE_1.length=N_BGC-1;
									//跑回圈加入到SELECT中
									FORM1.BUGCODE_1.options[0].style.color="red";
										for(TC=0;TC<N_BGC-1;TC++)
										{
											FORM1.BUGCODE_1.options[TC].value=A_BGC[TC].split("#")[1];
											FORM1.BUGCODE_1.options[TC].text="【"+A_BGC[TC].split("#")[1]+"】"+A_BGC[TC].split("#")[2];
										}
									
								}
								
--- SCRIPT ---

									FORM1.D_APYKIND_1.length=T_N_AK;
									for(AK=0;AK<T_N_AK-1;AK++)
									{
										FORM1.D_APYKIND_1.options[AK+1].value=T_A_AK[AK].split("$")[0];
										FORM1.D_APYKIND_1.options[AK+1].text=T_A_AK[AK].split("$")[0]+"【"+T_A_AK[AK].split("$")[1]+"】";
									}
									
								
--- SCRIPT ---

										function SERSUBJ_1()
										{
											
											//980902karen==>輸入科目轉成大寫及檢驗會計科目是否屬下拉清單有的											
											FORM1.SERSUB_1.value=FORM1.SUBJECTNO_1.value.toUpperCase();
											FORM1.SUBJECTNO_1.value=FORM1.SUBJECTNO_1.value.toUpperCase();
											NO_MSG_1="N"
										    if (!FORM1.SUBJECTNO_1.value=="" && FORM1.SERSUB_1.value=="")
										    {
										     alert("請填入或下拉選擇正確的會計科目!!!");
											 
											 //1030903Pan==>依輸入科目停在最近似的會計科目==>start
											 S_1_LEN=FORM1.SUBJECTNO_1.value.length;
											 for(i=0;i<FORM1.SERSUB_1.length;i++)
											 {
												if (FORM1.SUBJECTNO_1.value.toUpperCase()==FORM1.SERSUB_1[i].value.substr(0,S_1_LEN))
													{
														FORM1.SERSUB_1[i].selected=true;
														FORM1.SUBJECTNO_1.value="";
														NO_MSG_1="N"
														return;
													}
												else
												   {
												    NO_MSG_1="Y"
												   }
										    }
											if(NO_MSG_1="Y")
											{
											  FORM1.SUBJECTNO_1.value="";
											}
											//1030903Pan==>依輸入科目停在最近似的會計科目==>end
											
											}											
										}
									
--- SCRIPT ---

												
									function SS_1()
									{
										//定義select之option之數量
										FORM1.SERSUB_1.length=T_N_SJ;
										//跑回圈加入到SELECT中
										FORM1.SERSUB_1.options[0].value="";
										FORM1.SERSUB_1.options[0].text="查詢會計科目";
										FORM1.SERSUB_1.options[0].style.color="red";
										SJ_CO=1;
										for(TB=0;TB<T_N_SJ-1;TB++)
										{
											FORM1.SERSUB_1.options[TB+1].value=T_A_SJ[TB].split("#")[0];
											FORM1.SERSUB_1.options[TB+1].text="【"+T_A_SJ[TB].split("#")[0]+"】"+T_A_SJ[TB].split("#")[1];
										}										
									}
									
								
--- SCRIPT ---

										
									function BC_1()
									{
										var TMP_AM=0;
										
												parent.parent.LA_AM.FORM1.APYNO.value="";
												parent.parent.LA_AM.FORM1.APYADD.value="";
												parent.parent.LA_AM.FORM1.T_APYNO.value="";
												parent.parent.LA_AM.FORM1.T_APYADD.value="";
											
												//複製用
												parent.parent.LA_AM.FORM1.APYNO.value="";
												parent.parent.LA_AM.FORM1.APYADD.value="";
												parent.parent.LA_AM.FORM1.T_APYNO.value="";
												parent.parent.LA_AM.FORM1.T_APYADD.value="";
											
										parent.parent.LA_AM.FORM1.USERNO.value="56006";
										parent.parent.LA_AM.FORM1.BUGCODE.value=FORM1.BUGCODE_1.value;
										parent.parent.LA_AM.FORM1.BUGETNO.value=FORM1.BUGETNO_1.value;
										parent.parent.LA_AM.FORM1.INITMOVE.value=FORM1.MOVETYPE_1.value;
										
										parent.parent.LA_AM.FORM1.SUM_AM.value=TMP_AM;
										parent.parent.LA_AM.FORM1.RE_HAND.value="parent.MAIN.APPY.FORM1";
										parent.parent.LA_AM.FORM1.I_J.value="_1";
										parent.parent.LA_AM.FORM1.submit();
									}
								
--- SCRIPT ---

										function CA_1()
										{
												
												if (parseInt(FORM1.D_AMOUNT_1.value)>parseInt(FORM1.A9_1.value))
												{
													
														alert("所選金額已超出經費用途餘額,若確定以超出金額則點選【存入】!!");
													
												}
												
										}
										
								
--- SCRIPT ---

										FORM1.BUGETNO_2.length=N_CO_BUGET_VA;
										//跑回圈加入到SELECT中
										FORM1.BUGETNO_2.options[0].value="";
										FORM1.BUGETNO_2.options[0].text="請先【點選本格】下拉選擇經費";
										FORM1.BUGETNO_2.options[0].style.color="red";
										for(TB=0;TB<N_CO_BUGET_VA-1;TB++)
										{
											FORM1.BUGETNO_2.options[TB+1].value=A_CO_BUGET_VA[TB].split("#")[0];
											FORM1.BUGETNO_2.options[TB+1].text="【"+A_CO_BUGET_VA[TB].split("#")[0]+"】"+A_CO_BUGET_VA[TB].split("#")[1];
										}
											
									
--- SCRIPT ---

								
								//建立一個
								function BN_2()
								{
									var TQS_1="##下拉選擇經費用途#@";
									//將BUGETNO.VALUE送到HI
									for(TQ=0;TQ<T_N_BS-1;TQ++)
									{
										//組出可用之bugets之字串
										T_A_BS_A=T_A_BS[TQ].split("#");
										if(T_A_BS_A[0]==FORM1.BUGETNO_2.value)
										{
											TQS_1=TQS_1+T_A_BS[TQ]+"@";
										}
									}
									//再把字串切Array放到BUGCODE_?中
									A_BGC=new Array();
									A_BGC=TQS_1.split("@");
									N_BGC=A_BGC.length;
									//設定BUGCODE_之option數
										FORM1.BUGCODE_2.length=N_BGC-1;
										FORM1.BUGCODE_2.options[0].style.color="red";
										for(TC=0;TC<N_BGC-1;TC++)
										{
											FORM1.BUGCODE_2.options[TC].value=A_BGC[TC].split("#")[1];
											FORM1.BUGCODE_2.options[TC].text="【"+A_BGC[TC].split("#")[1]+"】"+A_BGC[TC].split("#")[2];
										}
																		
								}
								
--- SCRIPT ---

									FORM1.D_APYKIND_2.length=T_N_AK;
									for(AK=0;AK<T_N_AK-1;AK++)
									{
										FORM1.D_APYKIND_2.options[AK+1].value=T_A_AK[AK].split("$")[0];
										FORM1.D_APYKIND_2.options[AK+1].text=T_A_AK[AK].split("$")[0]+"【"+T_A_AK[AK].split("$")[1]+"】";
									}
									
								
--- SCRIPT ---

										function SERSUBJ_2()
										{
											//980902karen==>輸入科目轉成大寫及檢驗會計科目是否屬下拉清單有的
											FORM1.SERSUB_2.value=FORM1.SUBJECTNO_2.value.toUpperCase();
											FORM1.SUBJECTNO_2.value=FORM1.SUBJECTNO_2.value.toUpperCase();
											NO_MSG_2="N"
											if(!FORM1.SUBJECTNO_2.value=="" && FORM1.SERSUB_2.value=="")
											{
											 alert("請填入或下拉選擇正確的會計科目!!!");
											 
											 //1030903Pan==>依輸入科目停在最近似的會計科目==>start
											 S_2_LEN=FORM1.SUBJECTNO_2.value.length;
											 for(i=0;i<FORM1.SERSUB_2.length;i++)
											 {
												if (FORM1.SUBJECTNO_2.value.toUpperCase()==FORM1.SERSUB_2[i].value.substr(0,S_2_LEN))
													{
														FORM1.SERSUB_2[i].selected=true;
														FORM1.SUBJECTNO_2.value="";
														NO_MSG_2="N"
														return;
													}
												else
												   {
												    NO_MSG_2="Y"
												   }
										    }
											if(NO_MSG_2="Y")
											{
											  FORM1.SUBJECTNO_2.value="";
											}
											//1030903Pan==>依輸入科目停在最近似的會計科目==>end											 
											 
											}
										}
									
--- SCRIPT ---
		
									function SS_2()
									{
										//定義select之option之數量
										FORM1.SERSUB_2.length=T_N_SJ;
										//跑回圈加入到SELECT中
										FORM1.SERSUB_2.options[0].value="";
										FORM1.SERSUB_2.options[0].text="查詢會計科目";
										FORM1.SERSUB_2.options[0].style.color="red";
										SJ_CO=1
										for(TB=0;TB<T_N_SJ-1;TB++)
										{
											FORM1.SERSUB_2.options[TB+1].value=T_A_SJ[TB].split("#")[0];
											FORM1.SERSUB_2.options[TB+1].text="【"+T_A_SJ[TB].split("#")[0]+"】"+T_A_SJ[TB].split("#")[1];
										}
									}
									
								
--- SCRIPT ---

									function BC_2()
									{
										var TMP_AM=0;
										
											if(!FORM1.D_AMOUNT_1.value=="0")
											{
												if(FORM1.BUGCODE_2.value==FORM1.BUGCODE_1.value&&FORM1.BUGETNO_2.value==FORM1.BUGETNO_1.value)
												{
													TMP_AM=parseInt(TMP_AM)+parseInt(FORM1.D_AMOUNT_1.value);
												}
											}
										
												parent.parent.LA_AM.FORM1.APYNO.value="";
												parent.parent.LA_AM.FORM1.APYADD.value="";
												parent.parent.LA_AM.FORM1.T_APYNO.value="";
												parent.parent.LA_AM.FORM1.T_APYADD.value="";
											
												//複製用
												parent.parent.LA_AM.FORM1.APYNO.value="";
												parent.parent.LA_AM.FORM1.APYADD.value="";
												parent.parent.LA_AM.FORM1.T_APYNO.value="";
												parent.parent.LA_AM.FORM1.T_APYADD.value="";
											
										parent.parent.LA_AM.FORM1.USERNO.value="56006";
										parent.parent.LA_AM.FORM1.BUGCODE.value=FORM1.BUGCODE_2.value;
										parent.parent.LA_AM.FORM1.BUGETNO.value=FORM1.BUGETNO_2.value;
										parent.parent.LA_AM.FORM1.INITMOVE.value=FORM1.MOVETYPE_2.value;
										
										parent.parent.LA_AM.FORM1.SUM_AM.value=TMP_AM;
										parent.parent.LA_AM.FORM1.RE_HAND.value="parent.MAIN.APPY.FORM1";
										parent.parent.LA_AM.FORM1.I_J.value="_2";
										parent.parent.LA_AM.FORM1.submit();
									}
								
--- SCRIPT ---

										function CA_2()
										{
											if (parseInt(FORM1.D_AMOUNT_2.value)>parseInt(FORM1.A9_2.value))
											{
												
													alert("所選金額已超出經費用途餘額,若確定以超出金額則點選【存入】!!");
												
											}
										}
										
								
--- SCRIPT ---

										FORM1.BUGETNO_3.length=N_CO_BUGET_VA;
										//跑回圈加入到SELECT中
										FORM1.BUGETNO_3.options[0].value="";
										FORM1.BUGETNO_3.options[0].text="請先【點選本格】下拉選擇經費";
										FORM1.BUGETNO_3.options[0].style.color="red";
										for(TB=0;TB<N_CO_BUGET_VA-1;TB++)
										{
											FORM1.BUGETNO_3.options[TB+1].value=A_CO_BUGET_VA[TB].split("#")[0];
											FORM1.BUGETNO_3.options[TB+1].text="【"+A_CO_BUGET_VA[TB].split("#")[0]+"】"+A_CO_BUGET_VA[TB].split("#")[1];
										}
											
									
--- SCRIPT ---

								
								//建立一個
								function BN_3()
								{
									var TQS_1="##下拉選擇經費用途#@";
									//將BUGETNO.VALUE送到HI
									for(TQ=0;TQ<T_N_BS-1;TQ++)
									{
										//組出可用之bugets之字串
										T_A_BS_A=T_A_BS[TQ].split("#");
										if(T_A_BS_A[0]==FORM1.BUGETNO_3.value)
										{
											TQS_1=TQS_1+T_A_BS[TQ]+"@";
										}
									}
									//再把字串切Array放到BUGCODE_?中
									A_BGC=new Array();
									A_BGC=TQS_1.split("@");
									N_BGC=A_BGC.length;
									//設定BUGCODE_之option數
										FORM1.BUGCODE_3.length=N_BGC-1;
										FORM1.BUGCODE_3.options[0].style.color="red";
										for(TC=0;TC<N_BGC-1;TC++)
										{
											FORM1.BUGCODE_3.options[TC].value=A_BGC[TC].split("#")[1];
											FORM1.BUGCODE_3.options[TC].text="【"+A_BGC[TC].split("#")[1]+"】"+A_BGC[TC].split("#")[2];
										}
																		
								}
								
--- SCRIPT ---

									FORM1.D_APYKIND_3.length=T_N_AK;
									for(AK=0;AK<T_N_AK-1;AK++)
									{
										FORM1.D_APYKIND_3.options[AK+1].value=T_A_AK[AK].split("$")[0];
										FORM1.D_APYKIND_3.options[AK+1].text=T_A_AK[AK].split("$")[0]+"【"+T_A_AK[AK].split("$")[1]+"】";
									}
									
								
--- SCRIPT ---

										function SERSUBJ_3()
										{
											//980902karen==>輸入科目轉成大寫及檢驗會計科目是否屬下拉清單有的
											FORM1.SERSUB_3.value=FORM1.SUBJECTNO_3.value.toUpperCase();
											FORM1.SUBJECTNO_3.value=FORM1.SUBJECTNO_3.value.toUpperCase();
											NO_MSG_3="N"
											if(!FORM1.SUBJECTNO_3.value=="" && FORM1.SERSUB_3.value=="")
											{
											 alert("請填入或下拉選擇正確的會計科目!!!");
											 
											 //1030903Pan==>依輸入科目停在最近似的會計科目==>start
											 S_3_LEN=FORM1.SUBJECTNO_3.value.length;
											 for(i=0;i<FORM1.SERSUB_3.length;i++)
											 {
												if (FORM1.SUBJECTNO_3.value.toUpperCase()==FORM1.SERSUB_3[i].value.substr(0,S_3_LEN))
													{
														FORM1.SERSUB_3[i].selected=true;
														FORM1.SUBJECTNO_3.value="";
														NO_MSG_3="N"
														return;
													}
												else
												   {
												    NO_MSG_3="Y"
												   }
										    }
											if(NO_MSG_3="Y")
											{
											  FORM1.SUBJECTNO_3.value="";
											}
											//1030903Pan==>依輸入科目停在最近似的會計科目==>end											 
											 
											}
										}
									
--- SCRIPT ---
		
									function SS_3()
									{
										//定義select之option之數量
										FORM1.SERSUB_3.length=T_N_SJ;
										//跑回圈加入到SELECT中
										FORM1.SERSUB_3.options[0].value="";
										FORM1.SERSUB_3.options[0].text="查詢會計科目";
										FORM1.SERSUB_3.options[0].style.color="red";
										SJ_CO=1
										for(TB=0;TB<T_N_SJ-1;TB++)
										{
											FORM1.SERSUB_3.options[TB+1].value=T_A_SJ[TB].split("#")[0];
											FORM1.SERSUB_3.options[TB+1].text="【"+T_A_SJ[TB].split("#")[0]+"】"+T_A_SJ[TB].split("#")[1];
										}
									}
									
								
--- SCRIPT ---

									function BC_3()
									{
										var TMP_AM=0;
										
											if(!FORM1.D_AMOUNT_1.value=="0")
											{
												if(FORM1.BUGCODE_3.value==FORM1.BUGCODE_1.value&&FORM1.BUGETNO_3.value==FORM1.BUGETNO_1.value)
												{
													TMP_AM=parseInt(TMP_AM)+parseInt(FORM1.D_AMOUNT_1.value);
												}
											}
										
											if(!FORM1.D_AMOUNT_2.value=="0")
											{
												if(FORM1.BUGCODE_3.value==FORM1.BUGCODE_2.value&&FORM1.BUGETNO_3.value==FORM1.BUGETNO_2.value)
												{
													TMP_AM=parseInt(TMP_AM)+parseInt(FORM1.D_AMOUNT_2.value);
												}
											}
										
												parent.parent.LA_AM.FORM1.APYNO.value="";
												parent.parent.LA_AM.FORM1.APYADD.value="";
												parent.parent.LA_AM.FORM1.T_APYNO.value="";
												parent.parent.LA_AM.FORM1.T_APYADD.value="";
											
												//複製用
												parent.parent.LA_AM.FORM1.APYNO.value="";
												parent.parent.LA_AM.FORM1.APYADD.value="";
												parent.parent.LA_AM.FORM1.T_APYNO.value="";
												parent.parent.LA_AM.FORM1.T_APYADD.value="";
											
										parent.parent.LA_AM.FORM1.USERNO.value="56006";
										parent.parent.LA_AM.FORM1.BUGCODE.value=FORM1.BUGCODE_3.value;
										parent.parent.LA_AM.FORM1.BUGETNO.value=FORM1.BUGETNO_3.value;
										parent.parent.LA_AM.FORM1.INITMOVE.value=FORM1.MOVETYPE_3.value;
										
										parent.parent.LA_AM.FORM1.SUM_AM.value=TMP_AM;
										parent.parent.LA_AM.FORM1.RE_HAND.value="parent.MAIN.APPY.FORM1";
										parent.parent.LA_AM.FORM1.I_J.value="_3";
										parent.parent.LA_AM.FORM1.submit();
									}
								
--- SCRIPT ---

										function CA_3()
										{
											if (parseInt(FORM1.D_AMOUNT_3.value)>parseInt(FORM1.A9_3.value))
											{
												
													alert("所選金額已超出經費用途餘額,若確定以超出金額則點選【存入】!!");
												
											}
										}
										
								
--- SCRIPT ---

										FORM1.BUGETNO_4.length=N_CO_BUGET_VA;
										//跑回圈加入到SELECT中
										FORM1.BUGETNO_4.options[0].value="";
										FORM1.BUGETNO_4.options[0].text="請先【點選本格】下拉選擇經費";
										FORM1.BUGETNO_4.options[0].style.color="red";
										for(TB=0;TB<N_CO_BUGET_VA-1;TB++)
										{
											FORM1.BUGETNO_4.options[TB+1].value=A_CO_BUGET_VA[TB].split("#")[0];
											FORM1.BUGETNO_4.options[TB+1].text="【"+A_CO_BUGET_VA[TB].split("#")[0]+"】"+A_CO_BUGET_VA[TB].split("#")[1];
										}
											
									
--- SCRIPT ---

								
								//建立一個
								function BN_4()
								{
									var TQS_1="##下拉選擇經費用途#@";
									//將BUGETNO.VALUE送到HI
									for(TQ=0;TQ<T_N_BS-1;TQ++)
									{
										//組出可用之bugets之字串
										T_A_BS_A=T_A_BS[TQ].split("#");
										if(T_A_BS_A[0]==FORM1.BUGETNO_4.value)
										{
											TQS_1=TQS_1+T_A_BS[TQ]+"@";
										}
									}
									//再把字串切Array放到BUGCODE_?中
									A_BGC=new Array();
									A_BGC=TQS_1.split("@");
									N_BGC=A_BGC.length;
									//設定BUGCODE_之option數
										FORM1.BUGCODE_4.length=N_BGC-1;
										FORM1.BUGCODE_4.options[0].style.color="red";
										for(TC=0;TC<N_BGC-1;TC++)
										{
											FORM1.BUGCODE_4.options[TC].value=A_BGC[TC].split("#")[1];
											FORM1.BUGCODE_4.options[TC].text="【"+A_BGC[TC].split("#")[1]+"】"+A_BGC[TC].split("#")[2];
										}
																		
								}
								
--- SCRIPT ---

									FORM1.D_APYKIND_4.length=T_N_AK;
									for(AK=0;AK<T_N_AK-1;AK++)
									{
										FORM1.D_APYKIND_4.options[AK+1].value=T_A_AK[AK].split("$")[0];
										FORM1.D_APYKIND_4.options[AK+1].text=T_A_AK[AK].split("$")[0]+"【"+T_A_AK[AK].split("$")[1]+"】";
									}
									
								
--- SCRIPT ---

										function SERSUBJ_4()
										{
											//980902karen==>輸入科目轉成大寫及檢驗會計科目是否屬下拉清單有的
											FORM1.SERSUB_4.value=FORM1.SUBJECTNO_4.value.toUpperCase();
											FORM1.SUBJECTNO_4.value=FORM1.SUBJECTNO_4.value.toUpperCase();
											NO_MSG_4="N"
											if(!FORM1.SUBJECTNO_4.value=="" && FORM1.SERSUB_4.value=="")
											{
											 alert("請填入或下拉選擇正確的會計科目!!!");
											 
											 //1030903Pan==>依輸入科目停在最近似的會計科目==>start
											 S_4_LEN=FORM1.SUBJECTNO_4.value.length;
											 for(i=0;i<FORM1.SERSUB_4.length;i++)
											 {
												if (FORM1.SUBJECTNO_4.value.toUpperCase()==FORM1.SERSUB_4[i].value.substr(0,S_4_LEN))
													{
														FORM1.SERSUB_4[i].selected=true;
														FORM1.SUBJECTNO_4.value="";
														NO_MSG_4="N"
														return;
													}
												else
												   {
												    NO_MSG_4="Y"
												   }
										    }
											if(NO_MSG_4="Y")
											{
											  FORM1.SUBJECTNO_4.value="";
											}
											//1030903Pan==>依輸入科目停在最近似的會計科目==>end											 
											 
											}
										}
									
--- SCRIPT ---
		
									function SS_4()
									{
										//定義select之option之數量
										FORM1.SERSUB_4.length=T_N_SJ;
										//跑回圈加入到SELECT中
										FORM1.SERSUB_4.options[0].value="";
										FORM1.SERSUB_4.options[0].text="查詢會計科目";
										FORM1.SERSUB_4.options[0].style.color="red";
										SJ_CO=1
										for(TB=0;TB<T_N_SJ-1;TB++)
										{
											FORM1.SERSUB_4.options[TB+1].value=T_A_SJ[TB].split("#")[0];
											FORM1.SERSUB_4.options[TB+1].text="【"+T_A_SJ[TB].split("#")[0]+"】"+T_A_SJ[TB].split("#")[1];
										}
									}
									
								
--- SCRIPT ---

									function BC_4()
									{
										var TMP_AM=0;
										
											if(!FORM1.D_AMOUNT_1.value=="0")
											{
												if(FORM1.BUGCODE_4.value==FORM1.BUGCODE_1.value&&FORM1.BUGETNO_4.value==FORM1.BUGETNO_1.value)
												{
													TMP_AM=parseInt(TMP_AM)+parseInt(FORM1.D_AMOUNT_1.value);
												}
											}
										
											if(!FORM1.D_AMOUNT_2.value=="0")
											{
												if(FORM1.BUGCODE_4.value==FORM1.BUGCODE_2.value&&FORM1.BUGETNO_4.value==FORM1.BUGETNO_2.value)
												{
													TMP_AM=parseInt(TMP_AM)+parseInt(FORM1.D_AMOUNT_2.value);
												}
											}
										
											if(!FORM1.D_AMOUNT_3.value=="0")
											{
												if(FORM1.BUGCODE_4.value==FORM1.BUGCODE_3.value&&FORM1.BUGETNO_4.value==FORM1.BUGETNO_3.value)
												{
													TMP_AM=parseInt(TMP_AM)+parseInt(FORM1.D_AMOUNT_3.value);
												}
											}
										
												parent.parent.LA_AM.FORM1.APYNO.value="";
												parent.parent.LA_AM.FORM1.APYADD.value="";
												parent.parent.LA_AM.FORM1.T_APYNO.value="";
												parent.parent.LA_AM.FORM1.T_APYADD.value="";
											
												//複製用
												parent.parent.LA_AM.FORM1.APYNO.value="";
												parent.parent.LA_AM.FORM1.APYADD.value="";
												parent.parent.LA_AM.FORM1.T_APYNO.value="";
												parent.parent.LA_AM.FORM1.T_APYADD.value="";
											
										parent.parent.LA_AM.FORM1.USERNO.value="56006";
										parent.parent.LA_AM.FORM1.BUGCODE.value=FORM1.BUGCODE_4.value;
										parent.parent.LA_AM.FORM1.BUGETNO.value=FORM1.BUGETNO_4.value;
										parent.parent.LA_AM.FORM1.INITMOVE.value=FORM1.MO