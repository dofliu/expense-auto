function SUM_ALERT()
                        {
                          
									//alert("清單筆數太多(超過100),請耐心等候!!!");
						  
						  parent.DD.rows="0,*";
						  
						  	parent.QQ.cols="0,0,*";
						  
						      //將APPY,APPA,APPP之資料組給PR_SAVE
                                  
                              
						  parent.PS.FORM1.SAMPLENO.value=FORM1.SAMPLENO.value;
						  parent.PS.FORM1.APPU.value=FORM1.APPU.value;
						  parent.PS.FORM1.IsNew.value=FORM1.IsNew.value;
						  parent.PS.FORM1.APPYYEAR.value=FORM1.APPYYEAR.value;
						  parent.PS.FORM1.APYNO.value=FORM1.APYNO.value;
						  parent.PS.FORM1.APYADD.value=FORM1.APYADD.value;
						  parent.PS.FORM1.ADATE.value=FORM1.ADATE.value;
						  parent.PS.FORM1.APYDEP.value=FORM1.APYDEP.value;
						  parent.PS.FORM1.APYUSERNO.value=FORM1.APYUSERNO.value;
						  parent.PS.FORM1.ISAPPY.value=FORM1.ISAPPY.value;
						  parent.PS.FORM1.ISVOUC.value=FORM1.ISVOUC.value;
						  parent.PS.FORM1.ISTEMP.value=FORM1.ISTEMP.value;
						  parent.PS.FORM1.ISCASH.value=FORM1.ISCASH.value;
						  parent.PS.FORM1.ISPURC.value=FORM1.ISPURC.value;
						  parent.PS.FORM1.APPYSET.value=FORM1.APPYSET.value;
						  parent.PS.FORM1.MOVETYPE.value=FORM1.MOVETYPE.value;
						  parent.PS.FORM1.SETNAME.value=FORM1.SETNAME.value;
						  parent.PS.FORM1.ABSTRACT.value=FORM1.ABSTRACT.value;
						  parent.PS.FORM1.NO_MATH.value=FORM1.NO_MATH.value;
						  parent.PS.FORM1.VOUSERNO.value=FORM1.VOU_SERNO.value;
						   
						   parent.PS.FORM1.ISPERI.value=FORM1.ISPERI.value;
						   parent.PS.FORM1.ISESS.value=FORM1.ISESS.value;
						   //1020710Karen==>APPY增加兩欄位
						   parent.PS.FORM1.Y_METHODS.value=FORM1.Y_METHODS.value;
						   parent.PS.FORM1.ACCORDING.value=FORM1.ACCORDING.value;
						  						   
						  //若金額是0且沒有會簽則不可存入
						  if(FORM1.ALL_DEPT.value=="")
						  {
							 if(FORM1.D_AMOUNT_1.value=="")
							 {
								alert("請購金額不得為0");
								parent.DD.rows="160,*";
						  		
						  			parent.QQ.cols="*,0,0";
								
								return;
							}
						  }
						  //APPYBUY
						  //990419Karen==>已經越來越多學校有用清冊,且以下購案類型已固定為清冊類型,故改直接由購案類別判斷
						 
						  //作APPY之部分
						  T_APPY="";
						  T_BUG_AMT=0;
						  
						  	if(!FORM1.BUGETNO_1.value==""&&!FORM1.BUGCODE_1.value==""&&!FORM1.D_AMOUNT_1.value=="")
							{
								
								
								T_APPY=T_APPY+"1#"+FORM1.BUGETNO_1.value+"#"+FORM1.BUGCODE_1.value+"#"+FORM1.D_AMOUNT_1.value+"#"+FORM1.D_APYKIND_1.value+"#"+FORM1.SUBJECTNO_1.value+"#"+FORM1.MOVETYPE_1.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_1.value);
							}
						  
						  	if(!FORM1.BUGETNO_2.value==""&&!FORM1.BUGCODE_2.value==""&&!FORM1.D_AMOUNT_2.value=="")
							{
								
								
								T_APPY=T_APPY+"2#"+FORM1.BUGETNO_2.value+"#"+FORM1.BUGCODE_2.value+"#"+FORM1.D_AMOUNT_2.value+"#"+FORM1.D_APYKIND_2.value+"#"+FORM1.SUBJECTNO_2.value+"#"+FORM1.MOVETYPE_2.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_2.value);
							}
						  
						  	if(!FORM1.BUGETNO_3.value==""&&!FORM1.BUGCODE_3.value==""&&!FORM1.D_AMOUNT_3.value=="")
							{
								
								
								T_APPY=T_APPY+"3#"+FORM1.BUGETNO_3.value+"#"+FORM1.BUGCODE_3.value+"#"+FORM1.D_AMOUNT_3.value+"#"+FORM1.D_APYKIND_3.value+"#"+FORM1.SUBJECTNO_3.value+"#"+FORM1.MOVETYPE_3.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_3.value);
							}
						  
						  	if(!FORM1.BUGETNO_4.value==""&&!FORM1.BUGCODE_4.value==""&&!FORM1.D_AMOUNT_4.value=="")
							{
								
								
								T_APPY=T_APPY+"4#"+FORM1.BUGETNO_4.value+"#"+FORM1.BUGCODE_4.value+"#"+FORM1.D_AMOUNT_4.value+"#"+FORM1.D_APYKIND_4.value+"#"+FORM1.SUBJECTNO_4.value+"#"+FORM1.MOVETYPE_4.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_4.value);
							}
						  
						  	if(!FORM1.BUGETNO_5.value==""&&!FORM1.BUGCODE_5.value==""&&!FORM1.D_AMOUNT_5.value=="")
							{
								
								
								T_APPY=T_APPY+"5#"+FORM1.BUGETNO_5.value+"#"+FORM1.BUGCODE_5.value+"#"+FORM1.D_AMOUNT_5.value+"#"+FORM1.D_APYKIND_5.value+"#"+FORM1.SUBJECTNO_5.value+"#"+FORM1.MOVETYPE_5.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_5.value);
							}
						  
						  	if(!FORM1.BUGETNO_6.value==""&&!FORM1.BUGCODE_6.value==""&&!FORM1.D_AMOUNT_6.value=="")
							{
								
								
								T_APPY=T_APPY+"6#"+FORM1.BUGETNO_6.value+"#"+FORM1.BUGCODE_6.value+"#"+FORM1.D_AMOUNT_6.value+"#"+FORM1.D_APYKIND_6.value+"#"+FORM1.SUBJECTNO_6.value+"#"+FORM1.MOVETYPE_6.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_6.value);
							}
						  
						  	if(!FORM1.BUGETNO_7.value==""&&!FORM1.BUGCODE_7.value==""&&!FORM1.D_AMOUNT_7.value=="")
							{
								
								
								T_APPY=T_APPY+"7#"+FORM1.BUGETNO_7.value+"#"+FORM1.BUGCODE_7.value+"#"+FORM1.D_AMOUNT_7.value+"#"+FORM1.D_APYKIND_7.value+"#"+FORM1.SUBJECTNO_7.value+"#"+FORM1.MOVETYPE_7.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_7.value);
							}
						  
						  	if(!FORM1.BUGETNO_8.value==""&&!FORM1.BUGCODE_8.value==""&&!FORM1.D_AMOUNT_8.value=="")
							{
								
								
								T_APPY=T_APPY+"8#"+FORM1.BUGETNO_8.value+"#"+FORM1.BUGCODE_8.value+"#"+FORM1.D_AMOUNT_8.value+"#"+FORM1.D_APYKIND_8.value+"#"+FORM1.SUBJECTNO_8.value+"#"+FORM1.MOVETYPE_8.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_8.value);
							}
						  
						  	if(!FORM1.BUGETNO_9.value==""&&!FORM1.BUGCODE_9.value==""&&!FORM1.D_AMOUNT_9.value=="")
							{
								
								
								T_APPY=T_APPY+"9#"+FORM1.BUGETNO_9.value+"#"+FORM1.BUGCODE_9.value+"#"+FORM1.D_AMOUNT_9.value+"#"+FORM1.D_APYKIND_9.value+"#"+FORM1.SUBJECTNO_9.value+"#"+FORM1.MOVETYPE_9.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_9.value);
							}
						  
						  	if(!FORM1.BUGETNO_10.value==""&&!FORM1.BUGCODE_10.value==""&&!FORM1.D_AMOUNT_10.value=="")
							{
								
								
								T_APPY=T_APPY+"10#"+FORM1.BUGETNO_10.value+"#"+FORM1.BUGCODE_10.value+"#"+FORM1.D_AMOUNT_10.value+"#"+FORM1.D_APYKIND_10.value+"#"+FORM1.SUBJECTNO_10.value+"#"+FORM1.MOVETYPE_10.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_10.value);
							}
						  
						  	if(!FORM1.BUGETNO_11.value==""&&!FORM1.BUGCODE_11.value==""&&!FORM1.D_AMOUNT_11.value=="")
							{
								
								
								T_APPY=T_APPY+"11#"+FORM1.BUGETNO_11.value+"#"+FORM1.BUGCODE_11.value+"#"+FORM1.D_AMOUNT_11.value+"#"+FORM1.D_APYKIND_11.value+"#"+FORM1.SUBJECTNO_11.value+"#"+FORM1.MOVETYPE_11.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_11.value);
							}
						  
						  	if(!FORM1.BUGETNO_12.value==""&&!FORM1.BUGCODE_12.value==""&&!FORM1.D_AMOUNT_12.value=="")
							{
								
								
								T_APPY=T_APPY+"12#"+FORM1.BUGETNO_12.value+"#"+FORM1.BUGCODE_12.value+"#"+FORM1.D_AMOUNT_12.value+"#"+FORM1.D_APYKIND_12.value+"#"+FORM1.SUBJECTNO_12.value+"#"+FORM1.MOVETYPE_12.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_12.value);
							}
						  
						  	if(!FORM1.BUGETNO_13.value==""&&!FORM1.BUGCODE_13.value==""&&!FORM1.D_AMOUNT_13.value=="")
							{
								
								
								T_APPY=T_APPY+"13#"+FORM1.BUGETNO_13.value+"#"+FORM1.BUGCODE_13.value+"#"+FORM1.D_AMOUNT_13.value+"#"+FORM1.D_APYKIND_13.value+"#"+FORM1.SUBJECTNO_13.value+"#"+FORM1.MOVETYPE_13.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_13.value);
							}
						  
						  	if(!FORM1.BUGETNO_14.value==""&&!FORM1.BUGCODE_14.value==""&&!FORM1.D_AMOUNT_14.value=="")
							{
								
								
								T_APPY=T_APPY+"14#"+FORM1.BUGETNO_14.value+"#"+FORM1.BUGCODE_14.value+"#"+FORM1.D_AMOUNT_14.value+"#"+FORM1.D_APYKIND_14.value+"#"+FORM1.SUBJECTNO_14.value+"#"+FORM1.MOVETYPE_14.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_14.value);
							}
						  
						  	if(!FORM1.BUGETNO_15.value==""&&!FORM1.BUGCODE_15.value==""&&!FORM1.D_AMOUNT_15.value=="")
							{
								
								
								T_APPY=T_APPY+"15#"+FORM1.BUGETNO_15.value+"#"+FORM1.BUGCODE_15.value+"#"+FORM1.D_AMOUNT_15.value+"#"+FORM1.D_APYKIND_15.value+"#"+FORM1.SUBJECTNO_15.value+"#"+FORM1.MOVETYPE_15.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_15.value);
							}
						  
						  	if(!FORM1.BUGETNO_16.value==""&&!FORM1.BUGCODE_16.value==""&&!FORM1.D_AMOUNT_16.value=="")
							{
								
								
								T_APPY=T_APPY+"16#"+FORM1.BUGETNO_16.value+"#"+FORM1.BUGCODE_16.value+"#"+FORM1.D_AMOUNT_16.value+"#"+FORM1.D_APYKIND_16.value+"#"+FORM1.SUBJECTNO_16.value+"#"+FORM1.MOVETYPE_16.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_16.value);
							}
						  
						  	if(!FORM1.BUGETNO_17.value==""&&!FORM1.BUGCODE_17.value==""&&!FORM1.D_AMOUNT_17.value=="")
							{
								
								
								T_APPY=T_APPY+"17#"+FORM1.BUGETNO_17.value+"#"+FORM1.BUGCODE_17.value+"#"+FORM1.D_AMOUNT_17.value+"#"+FORM1.D_APYKIND_17.value+"#"+FORM1.SUBJECTNO_17.value+"#"+FORM1.MOVETYPE_17.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_17.value);
							}
						  
						  	if(!FORM1.BUGETNO_18.value==""&&!FORM1.BUGCODE_18.value==""&&!FORM1.D_AMOUNT_18.value=="")
							{
								
								
								T_APPY=T_APPY+"18#"+FORM1.BUGETNO_18.value+"#"+FORM1.BUGCODE_18.value+"#"+FORM1.D_AMOUNT_18.value+"#"+FORM1.D_APYKIND_18.value+"#"+FORM1.SUBJECTNO_18.value+"#"+FORM1.MOVETYPE_18.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_18.value);
							}
						  
						  	if(!FORM1.BUGETNO_19.value==""&&!FORM1.BUGCODE_19.value==""&&!FORM1.D_AMOUNT_19.value=="")
							{
								
								
								T_APPY=T_APPY+"19#"+FORM1.BUGETNO_19.value+"#"+FORM1.BUGCODE_19.value+"#"+FORM1.D_AMOUNT_19.value+"#"+FORM1.D_APYKIND_19.value+"#"+FORM1.SUBJECTNO_19.value+"#"+FORM1.MOVETYPE_19.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_19.value);
							}
						  
						  	if(!FORM1.BUGETNO_20.value==""&&!FORM1.BUGCODE_20.value==""&&!FORM1.D_AMOUNT_20.value=="")
							{
								
								
								T_APPY=T_APPY+"20#"+FORM1.BUGETNO_20.value+"#"+FORM1.BUGCODE_20.value+"#"+FORM1.D_AMOUNT_20.value+"#"+FORM1.D_APYKIND_20.value+"#"+FORM1.SUBJECTNO_20.value+"#"+FORM1.MOVETYPE_20.value+"@"
						  		T_BUG_AMT=T_BUG_AMT+parseInt(FORM1.D_AMOUNT_20.value);
							}
						  
						  parent.PS.FORM1.D_STR.value=T_APPY;
					
						  //作APPA之部分
						  T_APPA="";
						  TMA_AMOUNT=0;
						  //先判斷是否APPA只有一個若是則將第一個之AMOUNT定為T_BUG_AMT
						  //karen970426==>清冊有代墊人,金額不自動帶總額,依各明細輸入金額為準
						  
						  if(parent.APPA.FORM1.VENNAME_2.value=="")
						  {
						  	if( FORM1.NO_MATH.value=="N")
							{
							  parent.APPA.FORM1.AMOUNT_1.value=T_BUG_AMT;
							 }							
						  }		
						  
						  	if(!parent.APPA.FORM1.VENNAME_1.value=="" && !parent.APPA.FORM1.VENDORID_1.value=="")
							{
								T_APPA=T_APPA+"1#"+AscToChar(parent.APPA.FORM1.VENDORID_1.value)+"#"+parent.APPA.FORM1.VENNAME_1.value+"#"+parent.APPA.FORM1.IDATE_1.value+"#"+parent.APPA.FORM1.INVOICENO_1.value+"#"+parent.APPA.FORM1.AMOUNT_1.value+"#"+parent.APPA.FORM1.TAX_1.value+"#"+parent.APPA.FORM1.PAYKIND_1.value+"#"+parent.APPA.FORM1.BANKNO_1.value+"#"+parent.APPA.FORM1.ACCOUNT_1.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_1.value+"#"+parent.APPA.FORM1.I_VENDORID_1.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_1.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_2.value=="" && !parent.APPA.FORM1.VENDORID_2.value=="")
							{
								T_APPA=T_APPA+"2#"+AscToChar(parent.APPA.FORM1.VENDORID_2.value)+"#"+parent.APPA.FORM1.VENNAME_2.value+"#"+parent.APPA.FORM1.IDATE_2.value+"#"+parent.APPA.FORM1.INVOICENO_2.value+"#"+parent.APPA.FORM1.AMOUNT_2.value+"#"+parent.APPA.FORM1.TAX_2.value+"#"+parent.APPA.FORM1.PAYKIND_2.value+"#"+parent.APPA.FORM1.BANKNO_2.value+"#"+parent.APPA.FORM1.ACCOUNT_2.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_2.value+"#"+parent.APPA.FORM1.I_VENDORID_2.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_2.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_3.value=="" && !parent.APPA.FORM1.VENDORID_3.value=="")
							{
								T_APPA=T_APPA+"3#"+AscToChar(parent.APPA.FORM1.VENDORID_3.value)+"#"+parent.APPA.FORM1.VENNAME_3.value+"#"+parent.APPA.FORM1.IDATE_3.value+"#"+parent.APPA.FORM1.INVOICENO_3.value+"#"+parent.APPA.FORM1.AMOUNT_3.value+"#"+parent.APPA.FORM1.TAX_3.value+"#"+parent.APPA.FORM1.PAYKIND_3.value+"#"+parent.APPA.FORM1.BANKNO_3.value+"#"+parent.APPA.FORM1.ACCOUNT_3.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_3.value+"#"+parent.APPA.FORM1.I_VENDORID_3.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_3.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_4.value=="" && !parent.APPA.FORM1.VENDORID_4.value=="")
							{
								T_APPA=T_APPA+"4#"+AscToChar(parent.APPA.FORM1.VENDORID_4.value)+"#"+parent.APPA.FORM1.VENNAME_4.value+"#"+parent.APPA.FORM1.IDATE_4.value+"#"+parent.APPA.FORM1.INVOICENO_4.value+"#"+parent.APPA.FORM1.AMOUNT_4.value+"#"+parent.APPA.FORM1.TAX_4.value+"#"+parent.APPA.FORM1.PAYKIND_4.value+"#"+parent.APPA.FORM1.BANKNO_4.value+"#"+parent.APPA.FORM1.ACCOUNT_4.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_4.value+"#"+parent.APPA.FORM1.I_VENDORID_4.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_4.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_5.value=="" && !parent.APPA.FORM1.VENDORID_5.value=="")
							{
								T_APPA=T_APPA+"5#"+AscToChar(parent.APPA.FORM1.VENDORID_5.value)+"#"+parent.APPA.FORM1.VENNAME_5.value+"#"+parent.APPA.FORM1.IDATE_5.value+"#"+parent.APPA.FORM1.INVOICENO_5.value+"#"+parent.APPA.FORM1.AMOUNT_5.value+"#"+parent.APPA.FORM1.TAX_5.value+"#"+parent.APPA.FORM1.PAYKIND_5.value+"#"+parent.APPA.FORM1.BANKNO_5.value+"#"+parent.APPA.FORM1.ACCOUNT_5.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_5.value+"#"+parent.APPA.FORM1.I_VENDORID_5.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_5.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_6.value=="" && !parent.APPA.FORM1.VENDORID_6.value=="")
							{
								T_APPA=T_APPA+"6#"+AscToChar(parent.APPA.FORM1.VENDORID_6.value)+"#"+parent.APPA.FORM1.VENNAME_6.value+"#"+parent.APPA.FORM1.IDATE_6.value+"#"+parent.APPA.FORM1.INVOICENO_6.value+"#"+parent.APPA.FORM1.AMOUNT_6.value+"#"+parent.APPA.FORM1.TAX_6.value+"#"+parent.APPA.FORM1.PAYKIND_6.value+"#"+parent.APPA.FORM1.BANKNO_6.value+"#"+parent.APPA.FORM1.ACCOUNT_6.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_6.value+"#"+parent.APPA.FORM1.I_VENDORID_6.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_6.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_7.value=="" && !parent.APPA.FORM1.VENDORID_7.value=="")
							{
								T_APPA=T_APPA+"7#"+AscToChar(parent.APPA.FORM1.VENDORID_7.value)+"#"+parent.APPA.FORM1.VENNAME_7.value+"#"+parent.APPA.FORM1.IDATE_7.value+"#"+parent.APPA.FORM1.INVOICENO_7.value+"#"+parent.APPA.FORM1.AMOUNT_7.value+"#"+parent.APPA.FORM1.TAX_7.value+"#"+parent.APPA.FORM1.PAYKIND_7.value+"#"+parent.APPA.FORM1.BANKNO_7.value+"#"+parent.APPA.FORM1.ACCOUNT_7.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_7.value+"#"+parent.APPA.FORM1.I_VENDORID_7.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_7.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_8.value=="" && !parent.APPA.FORM1.VENDORID_8.value=="")
							{
								T_APPA=T_APPA+"8#"+AscToChar(parent.APPA.FORM1.VENDORID_8.value)+"#"+parent.APPA.FORM1.VENNAME_8.value+"#"+parent.APPA.FORM1.IDATE_8.value+"#"+parent.APPA.FORM1.INVOICENO_8.value+"#"+parent.APPA.FORM1.AMOUNT_8.value+"#"+parent.APPA.FORM1.TAX_8.value+"#"+parent.APPA.FORM1.PAYKIND_8.value+"#"+parent.APPA.FORM1.BANKNO_8.value+"#"+parent.APPA.FORM1.ACCOUNT_8.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_8.value+"#"+parent.APPA.FORM1.I_VENDORID_8.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_8.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_9.value=="" && !parent.APPA.FORM1.VENDORID_9.value=="")
							{
								T_APPA=T_APPA+"9#"+AscToChar(parent.APPA.FORM1.VENDORID_9.value)+"#"+parent.APPA.FORM1.VENNAME_9.value+"#"+parent.APPA.FORM1.IDATE_9.value+"#"+parent.APPA.FORM1.INVOICENO_9.value+"#"+parent.APPA.FORM1.AMOUNT_9.value+"#"+parent.APPA.FORM1.TAX_9.value+"#"+parent.APPA.FORM1.PAYKIND_9.value+"#"+parent.APPA.FORM1.BANKNO_9.value+"#"+parent.APPA.FORM1.ACCOUNT_9.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_9.value+"#"+parent.APPA.FORM1.I_VENDORID_9.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_9.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_10.value=="" && !parent.APPA.FORM1.VENDORID_10.value=="")
							{
								T_APPA=T_APPA+"10#"+AscToChar(parent.APPA.FORM1.VENDORID_10.value)+"#"+parent.APPA.FORM1.VENNAME_10.value+"#"+parent.APPA.FORM1.IDATE_10.value+"#"+parent.APPA.FORM1.INVOICENO_10.value+"#"+parent.APPA.FORM1.AMOUNT_10.value+"#"+parent.APPA.FORM1.TAX_10.value+"#"+parent.APPA.FORM1.PAYKIND_10.value+"#"+parent.APPA.FORM1.BANKNO_10.value+"#"+parent.APPA.FORM1.ACCOUNT_10.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_10.value+"#"+parent.APPA.FORM1.I_VENDORID_10.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_10.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_11.value=="" && !parent.APPA.FORM1.VENDORID_11.value=="")
							{
								T_APPA=T_APPA+"11#"+AscToChar(parent.APPA.FORM1.VENDORID_11.value)+"#"+parent.APPA.FORM1.VENNAME_11.value+"#"+parent.APPA.FORM1.IDATE_11.value+"#"+parent.APPA.FORM1.INVOICENO_11.value+"#"+parent.APPA.FORM1.AMOUNT_11.value+"#"+parent.APPA.FORM1.TAX_11.value+"#"+parent.APPA.FORM1.PAYKIND_11.value+"#"+parent.APPA.FORM1.BANKNO_11.value+"#"+parent.APPA.FORM1.ACCOUNT_11.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_11.value+"#"+parent.APPA.FORM1.I_VENDORID_11.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_11.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_12.value=="" && !parent.APPA.FORM1.VENDORID_12.value=="")
							{
								T_APPA=T_APPA+"12#"+AscToChar(parent.APPA.FORM1.VENDORID_12.value)+"#"+parent.APPA.FORM1.VENNAME_12.value+"#"+parent.APPA.FORM1.IDATE_12.value+"#"+parent.APPA.FORM1.INVOICENO_12.value+"#"+parent.APPA.FORM1.AMOUNT_12.value+"#"+parent.APPA.FORM1.TAX_12.value+"#"+parent.APPA.FORM1.PAYKIND_12.value+"#"+parent.APPA.FORM1.BANKNO_12.value+"#"+parent.APPA.FORM1.ACCOUNT_12.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_12.value+"#"+parent.APPA.FORM1.I_VENDORID_12.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_12.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_13.value=="" && !parent.APPA.FORM1.VENDORID_13.value=="")
							{
								T_APPA=T_APPA+"13#"+AscToChar(parent.APPA.FORM1.VENDORID_13.value)+"#"+parent.APPA.FORM1.VENNAME_13.value+"#"+parent.APPA.FORM1.IDATE_13.value+"#"+parent.APPA.FORM1.INVOICENO_13.value+"#"+parent.APPA.FORM1.AMOUNT_13.value+"#"+parent.APPA.FORM1.TAX_13.value+"#"+parent.APPA.FORM1.PAYKIND_13.value+"#"+parent.APPA.FORM1.BANKNO_13.value+"#"+parent.APPA.FORM1.ACCOUNT_13.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_13.value+"#"+parent.APPA.FORM1.I_VENDORID_13.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_13.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_14.value=="" && !parent.APPA.FORM1.VENDORID_14.value=="")
							{
								T_APPA=T_APPA+"14#"+AscToChar(parent.APPA.FORM1.VENDORID_14.value)+"#"+parent.APPA.FORM1.VENNAME_14.value+"#"+parent.APPA.FORM1.IDATE_14.value+"#"+parent.APPA.FORM1.INVOICENO_14.value+"#"+parent.APPA.FORM1.AMOUNT_14.value+"#"+parent.APPA.FORM1.TAX_14.value+"#"+parent.APPA.FORM1.PAYKIND_14.value+"#"+parent.APPA.FORM1.BANKNO_14.value+"#"+parent.APPA.FORM1.ACCOUNT_14.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_14.value+"#"+parent.APPA.FORM1.I_VENDORID_14.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_14.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_15.value=="" && !parent.APPA.FORM1.VENDORID_15.value=="")
							{
								T_APPA=T_APPA+"15#"+AscToChar(parent.APPA.FORM1.VENDORID_15.value)+"#"+parent.APPA.FORM1.VENNAME_15.value+"#"+parent.APPA.FORM1.IDATE_15.value+"#"+parent.APPA.FORM1.INVOICENO_15.value+"#"+parent.APPA.FORM1.AMOUNT_15.value+"#"+parent.APPA.FORM1.TAX_15.value+"#"+parent.APPA.FORM1.PAYKIND_15.value+"#"+parent.APPA.FORM1.BANKNO_15.value+"#"+parent.APPA.FORM1.ACCOUNT_15.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_15.value+"#"+parent.APPA.FORM1.I_VENDORID_15.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_15.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_16.value=="" && !parent.APPA.FORM1.VENDORID_16.value=="")
							{
								T_APPA=T_APPA+"16#"+AscToChar(parent.APPA.FORM1.VENDORID_16.value)+"#"+parent.APPA.FORM1.VENNAME_16.value+"#"+parent.APPA.FORM1.IDATE_16.value+"#"+parent.APPA.FORM1.INVOICENO_16.value+"#"+parent.APPA.FORM1.AMOUNT_16.value+"#"+parent.APPA.FORM1.TAX_16.value+"#"+parent.APPA.FORM1.PAYKIND_16.value+"#"+parent.APPA.FORM1.BANKNO_16.value+"#"+parent.APPA.FORM1.ACCOUNT_16.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_16.value+"#"+parent.APPA.FORM1.I_VENDORID_16.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_16.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_17.value=="" && !parent.APPA.FORM1.VENDORID_17.value=="")
							{
								T_APPA=T_APPA+"17#"+AscToChar(parent.APPA.FORM1.VENDORID_17.value)+"#"+parent.APPA.FORM1.VENNAME_17.value+"#"+parent.APPA.FORM1.IDATE_17.value+"#"+parent.APPA.FORM1.INVOICENO_17.value+"#"+parent.APPA.FORM1.AMOUNT_17.value+"#"+parent.APPA.FORM1.TAX_17.value+"#"+parent.APPA.FORM1.PAYKIND_17.value+"#"+parent.APPA.FORM1.BANKNO_17.value+"#"+parent.APPA.FORM1.ACCOUNT_17.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_17.value+"#"+parent.APPA.FORM1.I_VENDORID_17.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_17.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_18.value=="" && !parent.APPA.FORM1.VENDORID_18.value=="")
							{
								T_APPA=T_APPA+"18#"+AscToChar(parent.APPA.FORM1.VENDORID_18.value)+"#"+parent.APPA.FORM1.VENNAME_18.value+"#"+parent.APPA.FORM1.IDATE_18.value+"#"+parent.APPA.FORM1.INVOICENO_18.value+"#"+parent.APPA.FORM1.AMOUNT_18.value+"#"+parent.APPA.FORM1.TAX_18.value+"#"+parent.APPA.FORM1.PAYKIND_18.value+"#"+parent.APPA.FORM1.BANKNO_18.value+"#"+parent.APPA.FORM1.ACCOUNT_18.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_18.value+"#"+parent.APPA.FORM1.I_VENDORID_18.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_18.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_19.value=="" && !parent.APPA.FORM1.VENDORID_19.value=="")
							{
								T_APPA=T_APPA+"19#"+AscToChar(parent.APPA.FORM1.VENDORID_19.value)+"#"+parent.APPA.FORM1.VENNAME_19.value+"#"+parent.APPA.FORM1.IDATE_19.value+"#"+parent.APPA.FORM1.INVOICENO_19.value+"#"+parent.APPA.FORM1.AMOUNT_19.value+"#"+parent.APPA.FORM1.TAX_19.value+"#"+parent.APPA.FORM1.PAYKIND_19.value+"#"+parent.APPA.FORM1.BANKNO_19.value+"#"+parent.APPA.FORM1.ACCOUNT_19.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_19.value+"#"+parent.APPA.FORM1.I_VENDORID_19.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_19.value);
							}
						  
						  	if(!parent.APPA.FORM1.VENNAME_20.value=="" && !parent.APPA.FORM1.VENDORID_20.value=="")
							{
								T_APPA=T_APPA+"20#"+AscToChar(parent.APPA.FORM1.VENDORID_20.value)+"#"+parent.APPA.FORM1.VENNAME_20.value+"#"+parent.APPA.FORM1.IDATE_20.value+"#"+parent.APPA.FORM1.INVOICENO_20.value+"#"+parent.APPA.FORM1.AMOUNT_20.value+"#"+parent.APPA.FORM1.TAX_20.value+"#"+parent.APPA.FORM1.PAYKIND_20.value+"#"+parent.APPA.FORM1.BANKNO_20.value+"#"+parent.APPA.FORM1.ACCOUNT_20.value+"#"+parent.APPA.FORM1.ACCOUNTNAM_20.value+"#"+parent.APPA.FORM1.I_VENDORID_20.value+"#"+"@";
						  		TMA_AMOUNT=TMA_AMOUNT+parseInt(parent.APPA.FORM1.AMOUNT_20.value);
							}
						  
						   parent.PS.FORM1.A_STR.value=T_APPA;
						  
						   if (T_APPA.length==0)
						   {
							A=confirm("受款人尚未編輯，要編輯受款人嗎?")
							if(A)
							{
								parent.APPA.FORM1.AMOUNT_1.value=T_BUG_AMT;
								parent.DD.rows="160,*";
						  		
						  			parent.QQ.cols="0,*,0";
								
								return;
							}
						   }
						  	//若是受款人有編輯則必需相符且不為會簽
							if(FORM1.ALL_DEPT.value=="" && FORM1.NO_MATH.value=="N" )
							{
								if(TMA_AMOUNT!=T_BUG_AMT && parseInt(T_APPA.length)!=0)
								{
									alert("【請購金額與受款人金額加總不相符合,請調整受款人明細金額與所使用經費金額相符】");
									parent.DD.rows="160,*";
						  			
						  				parent.QQ.cols="0,*,0";
									
									return;
								}
							}
						  
						  
	//start 必須判斷是STD_APPP,STD_WorkList,STD_TRAVEL-------------------------------------------------------------------------------------------- 
						  //作APPP之部分(財物請購)--------------------------
						  if(FORM1.APPYBUY.value==""||FORM1.APPYBUY.value=="1")
						  {
						  	T_APPP="";
						  	TMP_AMOUNT=0;
							 REAL_ITEMS=0;
							 
							//先判斷是否APPP只有一個若是則將第一個之AMOUNT定為T_BUG_AMT							
							//if(parent.APPP.FORM1.PRODUCT_2.value=="")							
						  	//{
							  //if(FORM1.NO_MATH.value=="N")
							  //{
						  		//parent.APPP.FORM1.AMOUNT_1.value=T_BUG_AMT;
							  //}
						  	//}	
							//1020605Karen==>多筆品項，剛好要清第二筆時，若用上述判斷方式，會出現將請購總額一直帶到第一筆的狀況，故需重新掃過品名明細
							ONEPICE="Y";
														   
							   if(parent.APPP.FORM1.PRODUCT_2.value!="")
							   {
							    ONEPICE="N";
							   }
														   
							   if(parent.APPP.FORM1.PRODUCT_3.value!="")
							   {
							    ONEPICE="N";
							   }
														   
							   if(parent.APPP.FORM1.PRODUCT_4.value!="")
							   {
							    ONEPICE="N";
							   }
														   
							   if(parent.APPP.FORM1.PRODUCT_5.value!="")
							   {
							    ONEPICE="N";
							   }
														   
							   if(parent.APPP.FORM1.PRODUCT_6.value!="")
							   {
							    ONEPICE="N";
							   }
														   
							   if(parent.APPP.FORM1.PRODUCT_7.value!="")
							   {
							    ONEPICE="N";
							   }
														   
							   if(parent.APPP.FORM1.PRODUCT_8.value!="")
							   {
							    ONEPICE="N";
							   }
														   
							   if(parent.APPP.FORM1.PRODUCT_9.value!="")
							   {
							    ONEPICE="N";
							   }
														   
							   if(parent.APPP.FORM1.PRODUCT_10.value!="")
							   {
							    ONEPICE="N";
							   }
														   
							   if(parent.APPP.FORM1.PRODUCT_11.value!="")
							   {
							    ONEPICE="N";
							   }
														   
							   if(parent.APPP.FORM1.PRODUCT_12.value!="")
							   {
							    ONEPICE="N";
							   }
														   
							   if(parent.APPP.FORM1.PRODUCT_13.value!="")
							   {
							    ONEPICE="N";
							   }
														   
							   if(parent.APPP.FORM1.PRODUCT_14.value!="")
							   {
							    ONEPICE="N";
							   }
														   
							   if(parent.APPP.FORM1.PRODUCT_15.value!="")
							   {
							    ONEPICE="N";
							   }
							
							if(ONEPICE=="Y" && FORM1.NO_MATH.value=="N")
						  	{
							  parent.APPP.FORM1.AMOUNT_1.value=T_BUG_AMT;
						  	}
							
						  	
						  		if(!parent.APPP.FORM1.PRODUCT_1.value==""&&!parent.APPP.FORM1.AMOUNT_1.value=="")
								{
								    
								      T_APPP=T_APPP+"1◎"+parent.APPP.FORM1.PRODUCT_1.value+"○"+parent.APPP.FORM1.PRODUCT1_1.value+"○"+parent.APPP.FORM1.PRODUCT2_1.value+"○"+"◎"+parent.APPP.FORM1.QUANTITY_1.value+"◎"+parent.APPP.FORM1.SERUNIT_1.value+"◎"+parent.APPP.FORM1.AMOUNT_1.value+"◎"+parent.APPP.FORM1.PLACE_1.value+"◎"+parent.APPP.FORM1.PTYPE_1.value+"◎"+parent.APPP.FORM1.KEEPER_1.value+"◎"+parent.APPP.FORM1.KEEPERID_1.value+"◎"+parent.APPP.FORM1.KEEPERDNO_1.value+"@";
								   
									TMP_AMOUNT=TMP_AMOUNT+parseFloat(parent.APPP.FORM1.AMOUNT_1.value);
									REAL_ITEMS=1;
						  		}
						  	
						  		if(!parent.APPP.FORM1.PRODUCT_2.value==""&&!parent.APPP.FORM1.AMOUNT_2.value=="")
								{
								    
								      T_APPP=T_APPP+"2◎"+parent.APPP.FORM1.PRODUCT_2.value+"○"+parent.APPP.FORM1.PRODUCT1_2.value+"○"+parent.APPP.FORM1.PRODUCT2_2.value+"○"+"◎"+parent.APPP.FORM1.QUANTITY_2.value+"◎"+parent.APPP.FORM1.SERUNIT_2.value+"◎"+parent.APPP.FORM1.AMOUNT_2.value+"◎"+parent.APPP.FORM1.PLACE_2.value+"◎"+parent.APPP.FORM1.PTYPE_2.value+"◎"+parent.APPP.FORM1.KEEPER_2.value+"◎"+parent.APPP.FORM1.KEEPERID_2.value+"◎"+parent.APPP.FORM1.KEEPERDNO_2.value+"@";
								   
									TMP_AMOUNT=TMP_AMOUNT+parseFloat(parent.APPP.FORM1.AMOUNT_2.value);
									REAL_ITEMS=2;
						  		}
						  	
						  		if(!parent.APPP.FORM1.PRODUCT_3.value==""&&!parent.APPP.FORM1.AMOUNT_3.value=="")
								{
								    
								      T_APPP=T_APPP+"3◎"+parent.APPP.FORM1.PRODUCT_3.value+"○"+parent.APPP.FORM1.PRODUCT1_3.value+"○"+parent.APPP.FORM1.PRODUCT2_3.value+"○"+"◎"+parent.APPP.FORM1.QUANTITY_3.value+"◎"+parent.APPP.FORM1.SERUNIT_3.value+"◎"+parent.APPP.FORM1.AMOUNT_3.value+"◎"+parent.APPP.FORM1.PLACE_3.value+"◎"+parent.APPP.FORM1.PTYPE_3.value+"◎"+parent.APPP.FORM1.KEEPER_3.value+"◎"+parent.APPP.FORM1.KEEPERID_3.value+"◎"+parent.APPP.FORM1.KEEPERDNO_3.value+"@";
								   
									TMP_AMOUNT=TMP_AMOUNT+parseFloat(parent.APPP.FORM1.AMOUNT_3.value);
									REAL_ITEMS=3;
						  		}
						  	
						  		if(!parent.APPP.FORM1.PRODUCT_4.value==""&&!parent.APPP.FORM1.AMOUNT_4.value=="")
								{
								    
								      T_APPP=T_APPP+"4◎"+parent.APPP.FORM1.PRODUCT_4.value+"○"+parent.APPP.FORM1.PRODUCT1_4.value+"○"+parent.APPP.FORM1.PRODUCT2_4.value+"○"+"◎"+parent.APPP.FORM1.QUANTITY_4.value+"◎"+parent.APPP.FORM1.SERUNIT_4.value+"◎"+parent.APPP.FORM1.AMOUNT_4.value+"◎"+parent.APPP.FORM1.PLACE_4.value+"◎"+parent.APPP.FORM1.PTYPE_4.value+"◎"+parent.APPP.FORM1.KEEPER_4.value+"◎"+parent.APPP.FORM1.KEEPERID_4.value+"◎"+parent.APPP.FORM1.KEEPERDNO_4.value+"@";
								   
									TMP_AMOUNT=TMP_AMOUNT+parseFloat(parent.APPP.FORM1.AMOUNT_4.value);
									REAL_ITEMS=4;
						  		}
						  	
						  		if(!parent.APPP.FORM1.PRODUCT_5.value==""&&!parent.APPP.FORM1.AMOUNT_5.value=="")
								{
								    
								      T_APPP=T_APPP+"5◎"+parent.APPP.FORM1.PRODUCT_5.value+"○"+parent.APPP.FORM1.PRODUCT1_5.value+"○"+parent.APPP.FORM1.PRODUCT2_5.value+"○"+"◎"+parent.APPP.FORM1.QUANTITY_5.value+"◎"+parent.APPP.FORM1.SERUNIT_5.value+"◎"+parent.APPP.FORM1.AMOUNT_5.value+"◎"+parent.APPP.FORM1.PLACE_5.value+"◎"+parent.APPP.FORM1.PTYPE_5.value+"◎"+parent.APPP.FORM1.KEEPER_5.value+"◎"+parent.APPP.FORM1.KEEPERID_5.value+"◎"+parent.APPP.FORM1.KEEPERDNO_5.value+"@";
								   
									TMP_AMOUNT=TMP_AMOUNT+parseFloat(parent.APPP.FORM1.AMOUNT_5.value);
									REAL_ITEMS=5;
						  		}
						  	
						  		if(!parent.APPP.FORM1.PRODUCT_6.value==""&&!parent.APPP.FORM1.AMOUNT_6.value=="")
								{
								    
								      T_APPP=T_APPP+"6◎"+parent.APPP.FORM1.PRODUCT_6.value+"○"+parent.APPP.FORM1.PRODUCT1_6.value+"○"+parent.APPP.FORM1.PRODUCT2_6.value+"○"+"◎"+parent.APPP.FORM1.QUANTITY_6.value+"◎"+parent.APPP.FORM1.SERUNIT_6.value+"◎"+parent.APPP.FORM1.AMOUNT_6.value+"◎"+parent.APPP.FORM1.PLACE_6.value+"◎"+parent.APPP.FORM1.PTYPE_6.value+"◎"+parent.APPP.FORM1.KEEPER_6.value+"◎"+parent.APPP.FORM1.KEEPERID_6.value+"◎"+parent.APPP.FORM1.KEEPERDNO_6.value+"@";
								   
									TMP_AMOUNT=TMP_AMOUNT+parseFloat(parent.APPP.FORM1.AMOUNT_6.value);
									REAL_ITEMS=6;
						  		}
						  	
						  		if(!parent.APPP.FORM1.PRODUCT_7.value==""&&!parent.APPP.FORM1.AMOUNT_7.value=="")
								{
								    
								      T_APPP=T_APPP+"7◎"+parent.APPP.FORM1.PRODUCT_7.value+"○"+parent.APPP.FORM1.PRODUCT1_7.value+"○"+parent.APPP.FORM1.PRODUCT2_7.value+"○"+"◎"+parent.APPP.FORM1.QUANTITY_7.value+"◎"+parent.APPP.FORM1.SERUNIT_7.value+"◎"+parent.APPP.FORM1.AMOUNT_7.value+"◎"+parent.APPP.FORM1.PLACE_7.value+"◎"+parent.APPP.FORM1.PTYPE_7.value+"◎"+parent.APPP.FORM1.KEEPER_7.value+"◎"+parent.APPP.FORM1.KEEPERID_7.value+"◎"+parent.APPP.FORM1.KEEPERDNO_7.value+"@";
								   
									TMP_AMOUNT=TMP_AMOUNT+parseFloat(parent.APPP.FORM1.AMOUNT_7.value);
									REAL_ITEMS=7;
						  		}
						  	
						  		if(!parent.APPP.FORM1.PRODUCT_8.value==""&&!parent.APPP.FORM1.AMOUNT_8.value=="")
								{
								    
								      T_APPP=T_APPP+"8◎"+parent.APPP.FORM1.PRODUCT_8.value+"○"+parent.APPP.FORM1.PRODUCT1_8.value+"○"+parent.APPP.FORM1.PRODUCT2_8.value+"○"+"◎"+parent.APPP.FORM1.QUANTITY_8.value+"◎"+parent.APPP.FORM1.SERUNIT_8.value+"◎"+parent.APPP.FORM1.AMOUNT_8.value+"◎"+parent.APPP.FORM1.PLACE_8.value+"◎"+parent.APPP.FORM1.PTYPE_8.value+"◎"+parent.APPP.FORM1.KEEPER_8.value+"◎"+parent.APPP.FORM1.KEEPERID_8.value+"◎"+parent.APPP.FORM1.KEEPERDNO_8.value+"@";
								   
									TMP_AMOUNT=TMP_AMOUNT+parseFloat(parent.APPP.FORM1.AMOUNT_8.value);
									REAL_ITEMS=8;
						  		}
						  	
						  		if(!parent.APPP.FORM1.PRODUCT_9.value==""&&!parent.APPP.FORM1.AMOUNT_9.value=="")
								{
								    
								      T_APPP=T_APPP+"9◎"+parent.APPP.FORM1.PRODUCT_9.value+"○"+parent.APPP.FORM1.PRODUCT1_9.value+"○"+parent.APPP.FORM1.PRODUCT2_9.value+"○"+"◎"+parent.APPP.FORM1.QUANTITY_9.value+"◎"+parent.APPP.FORM1.SERUNIT_9.value+"◎"+parent.APPP.FORM1.AMOUNT_9.value+"◎"+parent.APPP.FORM1.PLACE_9.value+"◎"+parent.APPP.FORM1.PTYPE_9.value+"◎"+parent.APPP.FORM1.KEEPER_9.value+"◎"+parent.APPP.FORM1.KEEPERID_9.value+"◎"+parent.APPP.FORM1.KEEPERDNO_9.value+"@";
								   
									TMP_AMOUNT=TMP_AMOUNT+parseFloat(parent.APPP.FORM1.AMOUNT_9.value);
									REAL_ITEMS=9;
						  		}
						  	
						  		if(!parent.APPP.FORM1.PRODUCT_10.value==""&&!parent.APPP.FORM1.AMOUNT_10.value=="")
								{
								    
								      T_APPP=T_APPP+"10◎"+parent.APPP.FORM1.PRODUCT_10.value+"○"+parent.APPP.FORM1.PRODUCT1_10.value+"○"+parent.APPP.FORM1.PRODUCT2_10.value+"○"+"◎"+parent.APPP.FORM1.QUANTITY_10.value+"◎"+parent.APPP.FORM1.SERUNIT_10.value+"◎"+parent.APPP.FORM1.AMOUNT_10.value+"◎"+parent.APPP.FORM1.PLACE_10.value+"◎"+parent.APPP.FORM1.PTYPE_10.value+"◎"+parent.APPP.FORM1.KEEPER_10.value+"◎"+parent.APPP.FORM1.KEEPERID_10.value+"◎"+parent.APPP.FORM1.KEEPERDNO_10.value+"@";
								   
									TMP_AMOUNT=TMP_AMOUNT+parseFloat(parent.APPP.FORM1.AMOUNT_10.value);
									REAL_ITEMS=10;
						  		}
						  	
						  		if(!parent.APPP.FORM1.PRODUCT_11.value==""&&!parent.APPP.FORM1.AMOUNT_11.value=="")
								{
								    
								      T_APPP=T_APPP+"11◎"+parent.APPP.FORM1.PRODUCT_11.value+"○"+parent.APPP.FORM1.PRODUCT1_11.value+"○"+parent.APPP.FORM1.PRODUCT2_11.value+"○"+"◎"+parent.APPP.FORM1.QUANTITY_11.value+"◎"+parent.APPP.FORM1.SERUNIT_11.value+"◎"+parent.APPP.FORM1.AMOUNT_11.value+"◎"+parent.APPP.FORM1.PLACE_11.value+"◎"+parent.APPP.FORM1.PTYPE_11.value+"◎"+parent.APPP.FORM1.KEEPER_11.value+"◎"+parent.APPP.FORM1.KEEPERID_11.value+"◎"+parent.APPP.FORM1.KEEPERDNO_11.value+"@";
								   
									TMP_AMOUNT=TMP_AMOUNT+parseFloat(parent.APPP.FORM1.AMOUNT_11.value);
									REAL_ITEMS=11;
						  		}
						  	
						  		if(!parent.APPP.FORM1.PRODUCT_12.value==""&&!parent.APPP.FORM1.AMOUNT_12.value=="")
								{
								    
								      T_APPP=T_APPP+"12◎"+parent.APPP.FORM1.PRODUCT_12.value+"○"+parent.APPP.FORM1.PRODUCT1_12.value+"○"+parent.APPP.FORM1.PRODUCT2_12.value+"○"+"◎"+parent.APPP.FORM1.QUANTITY_12.value+"◎"+parent.APPP.FORM1.SERUNIT_12.value+"◎"+parent.APPP.FORM1.AMOUNT_12.value+"◎"+parent.APPP.FORM1.PLACE_12.value+"◎"+parent.APPP.FORM1.PTYPE_12.value+"◎"+parent.APPP.FORM1.KEEPER_12.value+"◎"+parent.APPP.FORM1.KEEPERID_12.value+"◎"+parent.APPP.FORM1.KEEPERDNO_12.value+"@";
								   
									TMP_AMOUNT=TMP_AMOUNT+parseFloat(parent.APPP.FORM1.AMOUNT_12.value);
									REAL_ITEMS=12;
						  		}
						  	
						  		if(!parent.APPP.FORM1.PRODUCT_13.value==""&&!parent.APPP.FORM1.AMOUNT_13.value=="")
								{
								    
								      T_APPP=T_APPP+"13◎"+parent.APPP.FORM1.PRODUCT_13.value+"○"+parent.APPP.FORM1.PRODUCT1_13.value+"○"+parent.APPP.FORM1.PRODUCT2_13.value+"○"+"◎"+parent.APPP.FORM1.QUANTITY_13.value+"◎"+parent.APPP.FORM1.SERUNIT_13.value+"◎"+parent.APPP.FORM1.AMOUNT_13.value+"◎"+parent.APPP.FORM1.PLACE_13.value+"◎"+parent.APPP.FORM1.PTYPE_13.value+"◎"+parent.APPP.FORM1.KEEPER_13.value+"◎"+parent.APPP.FORM1.KEEPERID_13.value+"◎"+parent.APPP.FORM1.KEEPERDNO_13.value+"@";
								   
									TMP_AMOUNT=TMP_AMOUNT+parseFloat(parent.APPP.FORM1.AMOUNT_13.value);
									REAL_ITEMS=13;
						  		}
						  	
						  		if(!parent.APPP.FORM1.PRODUCT_14.value==""&&!parent.APPP.FORM1.AMOUNT_14.value=="")
								{
								    
								      T_APPP=T_APPP+"14◎"+parent.APPP.FORM1.PRODUCT_14.value+"○"+parent.APPP.FORM1.PRODUCT1_14.value+"○"+parent.APPP.FORM1.PRODUCT2_14.value+"○"+"◎"+parent.APPP.FORM1.QUANTITY_14.value+"◎"+parent.APPP.FORM1.SERUNIT_14.value+"◎"+parent.APPP.FORM1.AMOUNT_14.value+"◎"+parent.APPP.FORM1.PLACE_14.value+"◎"+parent.APPP.FORM1.PTYPE_14.value+"◎"+parent.APPP.FORM1.KEEPER_14.value+"◎"+parent.APPP.FORM1.KEEPERID_14.value+"◎"+parent.APPP.FORM1.KEEPERDNO_14.value+"@";
								   
									TMP_AMOUNT=TMP_AMOUNT+parseFloat(parent.APPP.FORM1.AMOUNT_14.value);
									REAL_ITEMS=14;
						  		}
						  	
						  		if(!parent.APPP.FORM1.PRODUCT_15.value==""&&!parent.APPP.FORM1.AMOUNT_15.value=="")
								{
								    
								      T_APPP=T_APPP+"15◎"+parent.APPP.FORM1.PRODUCT_15.value+"○"+parent.APPP.FORM1.PRODUCT1_15.value+"○"+parent.APPP.FORM1.PRODUCT2_15.value+"○"+"◎"+parent.APPP.FORM1.QUANTITY_15.value+"◎"+parent.APPP.FORM1.SERUNIT_15.value+"◎"+parent.APPP.FORM1.AMOUNT_15.value+"◎"+parent.APPP.FORM1.PLACE_15.value+"◎"+parent.APPP.FORM1.PTYPE_15.value+"◎"+parent.APPP.FORM1.KEEPER_15.value+"◎"+parent.APPP.FORM1.KEEPERID_15.value+"◎"+parent.APPP.FORM1.KEEPERDNO_15.value+"@";
								   
									TMP_AMOUNT=TMP_AMOUNT+parseFloat(parent.APPP.FORM1.AMOUNT_15.value);
									REAL_ITEMS=15;
						  		}
						  	
							   TMP_AMOUNT=Math.round(TMP_AMOUNT);							  						   
						 	
						  	if(FORM1.ALL_DEPT.value=="")
						  	{
						    	 //若是第一項詳如附件但第二項沒有打資料則判斷金額
								//'判斷是否是由採購介面+明細近來的,若是則H必須忽略計算'pan961213	
								if(parent.APPP.FORM1.PRODUCT_1.value!="詳如附件" && parent.APPP.FORM1.PRODUCT_1.value.substr(1,3)!="採購單" )
						  		{
									if(TMP_AMOUNT!=T_BUG_AMT  && FORM1.NO_MATH.value!="Y")
									{
										alert("【請購金額$"+T_BUG_AMT+"與品名加總金額$"+TMP_AMOUNT+"不相符合,請調整品名加總金額與所使用經費金額相符】");
										parent.DD.rows="160,*";
						  				
						  					parent.QQ.cols="*,0,0";
										
										return;
									}
						  		}
								//若是第一項詳如附件但第二項又有打資料則判斷金額
								if(parent.APPP.FORM1.PRODUCT_1.value=="詳如附件" && parent.APPP.FORM1.PRODUCT_2.value!="")
						  		{
									if(TMP_AMOUNT!=T_BUG_AMT  && FORM1.NO_MATH.value!="Y")
									{
										alert("【請購金額$"+T_BUG_AMT+"與品名加總金額$"+TMP_AMOUNT+"不相符合,請調整品名加總金額與所使用經費金額相符】");
										parent.DD.rows="160,*";
						  				
						  					parent.QQ.cols="*,0,0";
										
										return;
									}
						  		}
						  	}
						  	
						   	parent.PS.FORM1.P_STR.value=T_APPP;
							
							if (REAL_ITEMS>100)
							{alert("品項資料筆數較多(超過100筆),請耐心等候!!!");}
							
						  }
						  //作APPP之部分end--------------------------
						  //990419Karen==>已經越來越多學校有用清冊,且以下購案類型已固定為清冊類型,故改直接由購案類別判斷
			
	//end 必須判斷是STD_APPP,STD_WorkList,STD_TRAVEL-------------------------------------------------------------------------------------------- 
						 
					 
						  		parent.PS.FORM1.submit();
						}