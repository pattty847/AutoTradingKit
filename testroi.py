if self._type_indicator == "Favorites":
                if new_state == Qt.CheckState.Checked:
                    if self._data == []:
                        self._data = [new_data]
                        if not self.delegate or not self.table_model:
                            
                            self.table_model = PositionModel(self._data)
                            self.setModel(self.table_model)
                            
                            self.delegate = PositionItemDelegate(self)
                            self.setItemDelegate(self.delegate)

                            hor_header = self.horizontalHeader()
                            ver_header = self.verticalHeader()

                            hor_header.setSectionResizeMode(0, QHeaderView.Fixed)  
                            ver_header.setSectionResizeMode(0, QHeaderView.Fixed)  
                            hor_header.resizeSection(0, 45)  
                            ver_header.resizeSection(0, 45) 

                            hor_header.setSectionResizeMode(2, QHeaderView.Fixed) 
                            ver_header.setSectionResizeMode(2, QHeaderView.Fixed)  
                            hor_header.resizeSection(2, 45) 
                            ver_header.resizeSection(2, 45)  
                            
                            hor_header.setSectionResizeMode(1, QHeaderView.Stretch)  
                        else:
                            self.table_model.insertRow(0,new_data)
                    else: 
                        self.table_model.insertRow(0,new_data)
                    if _type_indicator != "Favorites":
                        self.dict_favorites = AppConfig.get_config_value(f"topbar._type_indicator.favorite")
                        if new_state == Qt.CheckState.Unchecked:
                            if _type_indicator not in list(self.dict_favorites.keys()):
                                self.dict_favorites[_type_indicator] = []
                            else:
                                if _type_indicator in self.dict_favorites[_type_indicator]:
                                    self.dict_favorites[_type_indicator].remove(_type_indicator)
                        else:
                            if _type_indicator not in list(self.dict_favorites.keys()):
                                self.dict_favorites[_type_indicator] = [_type_indicator]
                            else:
                                if _type_indicator not in self.dict_favorites[_type_indicator]:
                                    self.dict_favorites[_type_indicator].append(_type_indicator)
                        AppConfig.sig_set_single_data.emit((f"topbar._type_indicator.favorite.{_type_indicator}",self.dict_favorites[_type_indicator]))
                        self.dict_favorites = AppConfig.get_config_value(f"topbar._type_indicator.favorite")    
                    
                else:
                    for index,row in enumerate(self.data):
                        if row[1] == _type_indicator and row[5] == from_indicator_wg:
                            self.table_model.removeRow(index)
                            if _type_indicator != "Favorites":
                                self.dict_favorites = AppConfig.get_config_value(f"topbar._type_indicator.favorite")
                                if new_state == Qt.CheckState.Unchecked:
                                    if _type_indicator not in list(self.dict_favorites.keys()):
                                        self.dict_favorites[_type_indicator] = []
                                    else:
                                        if _type_indicator in self.dict_favorites[_type_indicator]:
                                            self.dict_favorites[_type_indicator].remove(_type_indicator)
                                else:
                                    if _type_indicator not in list(self.dict_favorites.keys()):
                                        self.dict_favorites[_type_indicator] = [_type_indicator]
                                    else:
                                        if _type_indicator not in self.dict_favorites[_type_indicator]:
                                            self.dict_favorites[_type_indicator].append(_type_indicator)
                                AppConfig.sig_set_single_data.emit((f"topbar._type_indicator.favorite.{_type_indicator}",self.dict_favorites[_type_indicator]))
                                self.dict_favorites = AppConfig.get_config_value(f"topbar._type_indicator.favorite")  
                            break